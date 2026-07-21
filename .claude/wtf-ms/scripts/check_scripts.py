#!/usr/bin/env python3
"""
check_scripts — "runnable by construction" checks for the code wtf-MS
generates in computational / data-analysis tasks. A post-processing script
that doesn't even parse, imports a hallucinated package, or is a silent stub
is worse than no script: the researcher discovers it only when it crashes.

For each generated file this checks, WITHOUT executing anything:

  Python (.py)
    * syntax        — ast.parse; a SyntaxError is a hard bug          -> ERROR
    * imports       — top-level imports that are neither stdlib, a
                      recognized scientific package, nor a sibling
                      script (likely a typo / hallucinated package)   -> WARN
    * stubs         — bare `...`, `raise NotImplementedError`,
                      pass-only functions, or template placeholders
                      (path/to/, YOUR_, <...>, TODO/FIXME)            -> WARN
  Shell (.sh, .bash)
    * syntax        — `bash -n`                                       -> ERROR

Nothing is imported or run, so this is safe on untrusted generated code and
has no environment dependencies (a package being importable in the user's
env is deliberately NOT required — that would false-positive in CI).

Exit status: non-zero if any ERROR. Zero third-party deps.

Usage:
  python3 .claude/wtf-ms/scripts/check_scripts.py .research/tasks/task-01/*.py
  python3 .claude/wtf-ms/scripts/check_scripts.py --json task-01-analysis.py
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys

# Common scientific / materials-science packages an analysis script may import.
# Anything here OR in sys.stdlib_module_names OR a sibling .py is "recognized".
KNOWN_PACKAGES = {
    "numpy", "np", "scipy", "pandas", "matplotlib", "mpl_toolkits", "seaborn",
    "sklearn", "skimage", "sympy", "statsmodels", "networkx", "numba", "cython",
    "h5py", "netCDF4", "xarray", "zarr", "plotly", "bokeh", "altair",
    "tensorflow", "torch", "keras", "jax", "jaxlib", "pint", "uncertainties",
    "lmfit", "tqdm", "requests", "yaml", "toml", "joblib", "numexpr", "dask",
    "ase", "pymatgen", "phonopy", "phono3py", "spglib", "MDAnalysis",
    "mdanalysis", "openmm", "rdkit", "pyvista", "vtk", "mayavi", "ovito",
    "atomman", "lammps", "gpaw", "abipy", "aiida", "monty", "click", "typer",
    "mp_api", "matminer", "fireworks", "custodian", "emmet", "pybamm",
    "fenics", "dolfin", "meshio", "gmsh", "pillow", "PIL", "cv2", "numpydoc",
    "pytest", "hypothesis", "sqlalchemy", "polars", "pyarrow",
}


class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, line, rule, msg):
        self.errors.append((path, line, rule, msg))

    def warn(self, path, line, rule, msg):
        self.warnings.append((path, line, rule, msg))


_PLACEHOLDER_TEXT = re.compile(
    r"path/to/|/path/to|YOUR_[A-Z]|<[a-z_]+>|\bTODO\b|\bFIXME\b|"
    r"REPLACE_ME|FILL_IN|XXXX", re.IGNORECASE)


def _top_module(name):
    return (name or "").split(".")[0]


def _stub_findings(tree, path, fnd):
    for node in ast.walk(tree):
        # bare `...` used as a statement (not numpy `a[...]` indexing)
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and node.value.value is Ellipsis):
            fnd.warn(path, node.lineno, "stub",
                     "bare `...` placeholder — body not implemented")
        if isinstance(node, ast.Raise):
            exc = node.exc
            name = None
            if isinstance(exc, ast.Call):
                name = getattr(exc.func, "id", None)
            elif isinstance(exc, ast.Name):
                name = exc.id
            if name == "NotImplementedError":
                fnd.warn(path, node.lineno, "stub",
                         "raises NotImplementedError — not implemented")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and \
                    isinstance(body[0].value, ast.Constant) and \
                    isinstance(body[0].value.value, str):
                body = body[1:]                    # drop docstring
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                fnd.warn(path, node.lineno, "stub",
                         f"function '{node.name}' has an empty (pass-only) body")


def check_python(text, path, fnd, local_modules):
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as e:
        fnd.error(path, e.lineno or 0, "syntax",
                  f"SyntaxError: {e.msg}")
        return
    # imports
    known = set(sys.stdlib_module_names) | KNOWN_PACKAGES | local_modules
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = _top_module(alias.name)
                if mod and mod not in known:
                    fnd.warn(path, node.lineno, "import",
                             f"'{mod}' is not stdlib or a recognized package "
                             "— check spelling / that it's real")
        elif isinstance(node, ast.ImportFrom):
            if node.level:                          # relative import: skip
                continue
            mod = _top_module(node.module)
            if mod and mod not in known:
                fnd.warn(path, node.lineno, "import",
                         f"'{mod}' is not stdlib or a recognized package "
                         "— check spelling / that it's real")
    # stubs (AST-based) + textual placeholders
    _stub_findings(tree, path, fnd)
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#") is False and _PLACEHOLDER_TEXT.search(line):
            m = _PLACEHOLDER_TEXT.search(line)
            fnd.warn(path, i, "placeholder",
                     f"template placeholder left in code: '{m.group(0)}'")
        elif line.lstrip().startswith("#") and _PLACEHOLDER_TEXT.search(line):
            # placeholders in comments are lower-signal but still worth noting
            m = _PLACEHOLDER_TEXT.search(line)
            fnd.warn(path, i, "placeholder",
                     f"placeholder in comment: '{m.group(0)}'")


def check_shell(path, fnd):
    try:
        r = subprocess.run(["bash", "-n", path], capture_output=True,
                           text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as e:
        fnd.warn(path, 0, "shell", f"could not run `bash -n`: {e}")
        return
    if r.returncode != 0:
        msg = (r.stderr or "").strip().splitlines()
        fnd.error(path, 0, "syntax",
                  "bash syntax error: " + (msg[-1] if msg else "see bash -n"))


def scan(paths):
    fnd = Findings()
    local_modules = {os.path.splitext(os.path.basename(p))[0]
                     for p in paths if p.endswith(".py")}
    for p in paths:
        try:
            if p.endswith(".py"):
                with open(p, encoding="utf-8") as f:
                    check_python(f.read(), p, fnd, local_modules)
            elif p.endswith((".sh", ".bash")):
                check_shell(p, fnd)
        except OSError as e:
            print(f"WARN: cannot read {p}: {e}", file=sys.stderr)
    return fnd


def main():
    ap = argparse.ArgumentParser(
        description="Runnable-by-construction checks for generated scripts.")
    ap.add_argument("paths", nargs="+", help=".py / .sh files to check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    fnd = scan(args.paths)

    if args.json:
        print(json.dumps({
            "errors": [{"file": p, "line": l, "rule": r, "message": m}
                       for p, l, r, m in fnd.errors],
            "warnings": [{"file": p, "line": l, "rule": r, "message": m}
                         for p, l, r, m in fnd.warnings],
        }, indent=2))
    else:
        def emit(items, label):
            if not items:
                return
            print(f"\n{label} ({len(items)}):")
            for p, l, r, m in sorted(items):
                loc = f"{p}:{l}" if l else p
                print(f"  {loc}  [{r}]  {m}")
        emit(fnd.errors, "WILL NOT RUN (errors)")
        emit(fnd.warnings, "SUSPECT (warnings)")
        n = len(fnd.errors) + len(fnd.warnings)
        print(f"\ncheck-scripts: {len(fnd.errors)} error(s), "
              f"{len(fnd.warnings)} warning(s)."
              + ("" if n else " Generated scripts parse cleanly."))

    return 1 if fnd.errors else 0


if __name__ == "__main__":
    sys.exit(main())
