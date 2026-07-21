# Runnable-by-construction checks

`computational` and `data-analysis` tasks generate code — a post-processing
`task-NN-analysis.py`, a `task-NN-run.sh` submission script. A script that
doesn't parse, imports a hallucinated package, or is a silent stub is worse
than no script: the researcher finds out only when it crashes.
`.claude/wtf-ms/scripts/check_scripts.py` checks generated scripts **without
executing them**, so it is safe on untrusted code and has no environment
dependencies.

## What it checks

| File | Rule | Severity | Catches |
|------|------|----------|---------|
| `.py` | `syntax` | error | anything that fails `ast.parse` — the script would not run |
| `.py` | `import` | warn | a top-level import that is neither stdlib, a recognized scientific package, nor a sibling script — likely a typo (`nummpy`) or hallucinated package |
| `.py` | `stub` | warn | bare `...`, `raise NotImplementedError`, or a pass-only function body |
| `.py` | `placeholder` | warn | template text left in code (`path/to/`, `YOUR_KEY`, `<endpoint>`, `TODO`) |
| `.sh`, `.bash` | `syntax` | error | anything that fails `bash -n` |

It exits non-zero if any **error** is present.

## Static checking, not importing

Importing a module runs its top-level code — unsafe on generated code and
dependent on what's installed. So imports are checked *statically*: a package
being importable in the user's environment is deliberately **not** required
(that would false-positive in CI or a fresh env). The import check only asks
"is this a real, correctly-spelled package name?", matching against
`sys.stdlib_module_names`, a curated list of common scientific/MS packages
(numpy, scipy, pandas, ase, pymatgen, MDAnalysis, …), and any sibling `.py`
being checked in the same run.

Recognized-package coverage is a curated set — a legitimate but niche package
can produce an `import` warning. That is advisory: confirm the spelling and
move on. Extend `KNOWN_PACKAGES` at the top of the script if a package recurs.

## When it runs

`/wtfMS:execute-task` runs it on a completed task's `.py`/`.sh` outputs as an
**advisory** step before committing — fix `WILL NOT RUN` errors, review
`SUSPECT` warnings. It never hard-blocks.

## Running it manually

```bash
python3 .claude/wtf-ms/scripts/check_scripts.py .research/tasks/task-01/*.py .research/tasks/task-01/*.sh
python3 .claude/wtf-ms/scripts/check_scripts.py --json task-01-analysis.py
```

Zero third-party dependencies.

## Limitations

- Parse-level, not runtime: it confirms the script *parses* and its imports
  *look real*; it does not confirm the logic is correct or that the script
  produces the intended result. That validation still needs a real run against
  real data.
- Input files in domain formats (VASP `INCAR`, LAMMPS input, `KPOINTS`) are not
  checked — there is no universal parser for them. Only `.py` and shell scripts
  are covered.
