#!/usr/bin/env python3
"""
wtfms-lint — static linter for the wtf-MS Claude Code command/agent system.

wtf-MS has no compiled code; its "source" is markdown command and agent
definitions plus templates/references. This linter checks the deterministic
surface of those files so structural breakage is caught before runtime:

  1. frontmatter    — parses; has name + description; name matches filename
  2. task-tool      — a command that spawns a subagent via Task(...) must
                      list `Task` in allowed-tools
  3. static-include — @.claude/... @-includes must resolve on disk
  4. agent-path     — .claude/agents/wtfMS/<x>.md paths referenced in a
                      command body must exist
  5. tool-names     — every allowed-tools entry is a known Claude Code tool
  6. state-include  — @.research/... @-includes name a known state file (warn)
  7. help-sync      — help.md lists exactly the set of commands (warn)

Errors fail CI (exit 1). Warnings are printed but do not fail.

Usage:  python3 scripts/lint.py [--repo ROOT]
Zero dependencies (stdlib only).
"""
import os
import re
import sys
import argparse

# ---- configuration --------------------------------------------------------

COMMANDS_DIR = ".claude/commands/wtfMS"
AGENTS_DIR = ".claude/agents/wtfMS"
HELP_FILE = ".claude/commands/wtfMS/help.md"

# Known Claude Code tool names an allowed-tools list may reference.
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "MultiEdit", "NotebookEdit",
    "Bash", "Glob", "Grep", "Task",
    "WebSearch", "WebFetch", "AskUserQuestion",
    "TodoWrite", "Skill",
}

# Top-level runtime state files the workflow generates under .research/.
# @.research/<x> includes are not existence-checked (they're created at
# runtime), but the name is sanity-checked against this allowlist to catch
# typos like @.research/WORKFLOWS.md.
KNOWN_STATE_FILES = {
    "RESEARCH.md", "LITERATURE.md", "WORKFLOW.md", "STATE.md",
    "VIRTUAL-LAB.md", "DATA-INDEX.md", "config.json",
}

# ---- finding plumbing -----------------------------------------------------

class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, path, rule, msg):
        self.errors.append((path, rule, msg))

    def warn(self, path, rule, msg):
        self.warnings.append((path, rule, msg))


# ---- frontmatter parsing --------------------------------------------------

def split_frontmatter(text):
    """Return (frontmatter_str, body_str) or (None, text) if no frontmatter."""
    if not text.startswith("---"):
        return None, text
    # match leading ---\n ... \n---
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def parse_frontmatter(fm):
    """
    Minimal YAML-subset parser for our frontmatter. Handles:
      key: value
      allowed-tools: []            (inline empty)
      allowed-tools:
        - Tool
        - Tool
    Returns dict; list-valued keys map to a Python list.
    """
    data = {}
    lines = fm.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "[]":
            data[key] = []
        elif val == "":
            # possibly a block list on following indented "- " lines
            items = []
            j = i + 1
            while j < len(lines) and re.match(r"^\s+-\s+", lines[j]):
                items.append(re.sub(r"^\s+-\s+", "", lines[j]).strip())
                j += 1
            if items:
                data[key] = items
                i = j
                continue
            data[key] = ""
        else:
            data[key] = val.strip().strip('"').strip("'")
        i += 1
    return data


# ---- checks ---------------------------------------------------------------

def check_command(path, text, fnd, command_basenames):
    rel = os.path.relpath(path)
    fm_str, body = split_frontmatter(text)

    # 1. frontmatter
    if fm_str is None:
        fnd.error(rel, "frontmatter", "no YAML frontmatter block found")
        return
    fm = parse_frontmatter(fm_str)

    name = fm.get("name")
    if not name:
        fnd.error(rel, "frontmatter", "missing required key: name")
    else:
        expected = "wtfMS:" + os.path.basename(path)[:-3]
        if name != expected:
            fnd.error(rel, "frontmatter",
                      f"name '{name}' should be '{expected}' (matches filename)")
    if not fm.get("description"):
        fnd.error(rel, "frontmatter", "missing required key: description")

    tools = fm.get("allowed-tools", None)
    if tools is None:
        fnd.error(rel, "frontmatter", "missing required key: allowed-tools")
        tools = []
    if not isinstance(tools, list):
        fnd.error(rel, "frontmatter", "allowed-tools must be a list (or [])")
        tools = []

    # 5. tool names
    for t in tools:
        if t not in KNOWN_TOOLS:
            fnd.error(rel, "tool-names",
                      f"unknown tool '{t}' in allowed-tools "
                      f"(known: {', '.join(sorted(KNOWN_TOOLS))})")

    # 2. task-tool: spawns subagent -> must allow Task
    spawns = bool(re.search(r"\bTask\s*\(", body)) or "subagent_type" in body
    if spawns and "Task" not in tools:
        fnd.error(rel, "task-tool",
                  "command invokes Task(...) to spawn a subagent but "
                  "'Task' is not in allowed-tools")

    # 4. agent-path references resolve
    _check_agent_paths(path, body, fnd, rel)

    # 3 & 6. @-includes
    _check_includes(path, body, fnd, rel)


def _check_agent_paths(path, body, fnd, rel):
    repo_root = _repo_root_from(path)
    for m in re.finditer(r"\.claude/agents/wtfMS/[\w-]+\.md", body):
        ref = m.group(0)
        if not os.path.isfile(os.path.join(repo_root, ref)):
            fnd.error(rel, "agent-path",
                      f"references agent file '{ref}' which does not exist")


def _check_includes(path, body, fnd, rel):
    repo_root = _repo_root_from(path)
    for m in re.finditer(r"@(\.[\w./-]+\.(?:md|json))", body):
        inc = m.group(1)  # e.g. .research/WORKFLOW.md or .claude/wtf-ms/...
        if inc.startswith(".claude/"):
            # 3. static include must resolve
            if not os.path.isfile(os.path.join(repo_root, inc)):
                fnd.error(rel, "static-include",
                          f"@-include '{inc}' does not exist on disk")
        elif inc.startswith(".research/"):
            # 6. runtime state include — sanity-check name only (warn)
            base = inc[len(".research/"):]
            if base not in KNOWN_STATE_FILES:
                fnd.warn(rel, "state-include",
                         f"@-include '{inc}' is not a known state file "
                         f"(known: {', '.join(sorted(KNOWN_STATE_FILES))})")
        else:
            fnd.warn(rel, "unknown-include",
                     f"@-include '{inc}' has an unrecognized prefix")


def check_agent(path, text, fnd):
    rel = os.path.relpath(path)
    fm_str, _ = split_frontmatter(text)
    if fm_str is None:
        fnd.error(rel, "frontmatter", "no YAML frontmatter block found")
        return
    fm = parse_frontmatter(fm_str)
    name = fm.get("name")
    if not name:
        fnd.error(rel, "frontmatter", "missing required key: name")
    elif not re.match(r"^wtfms-[\w-]+$", name):
        fnd.error(rel, "frontmatter",
                  f"agent name '{name}' should match 'wtfms-<slug>'")
    if not fm.get("description"):
        fnd.error(rel, "frontmatter", "missing required key: description")


def check_help_sync(repo_root, command_basenames, fnd):
    help_path = os.path.join(repo_root, HELP_FILE)
    rel = os.path.relpath(help_path)
    if not os.path.isfile(help_path):
        fnd.error(rel, "help-sync", "help.md not found")
        return
    with open(help_path, encoding="utf-8") as f:
        help_text = f.read()
    listed = set(re.findall(r"/wtfMS:([a-z][\w-]*)", help_text))
    actual = set(command_basenames)
    missing = actual - listed
    extra = listed - actual
    for name in sorted(missing):
        fnd.warn(rel, "help-sync",
                 f"command '/wtfMS:{name}' exists but is not listed in help.md")
    for name in sorted(extra):
        fnd.warn(rel, "help-sync",
                 f"help.md lists '/wtfMS:{name}' but no such command file exists")


# ---- helpers --------------------------------------------------------------

_REPO_ROOT = None

def _repo_root_from(path):
    return _REPO_ROOT


def main():
    global _REPO_ROOT
    ap = argparse.ArgumentParser(description="Static linter for wtf-MS.")
    ap.add_argument("--repo", default=None, help="repo root (default: auto)")
    args = ap.parse_args()

    repo_root = args.repo or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _REPO_ROOT = repo_root

    fnd = Findings()

    commands_dir = os.path.join(repo_root, COMMANDS_DIR)
    agents_dir = os.path.join(repo_root, AGENTS_DIR)

    if not os.path.isdir(commands_dir):
        print(f"FATAL: commands dir not found: {commands_dir}", file=sys.stderr)
        return 2

    command_files = sorted(
        f for f in os.listdir(commands_dir) if f.endswith(".md")
    )
    command_basenames = [f[:-3] for f in command_files]

    for f in command_files:
        p = os.path.join(commands_dir, f)
        with open(p, encoding="utf-8") as fh:
            check_command(p, fh.read(), fnd, command_basenames)

    if os.path.isdir(agents_dir):
        for f in sorted(os.listdir(agents_dir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(agents_dir, f)
            with open(p, encoding="utf-8") as fh:
                check_agent(p, fh.read(), fnd)

    check_help_sync(repo_root, command_basenames, fnd)

    # ---- report ----
    def emit(items, label):
        if not items:
            return
        print(f"\n{label} ({len(items)}):")
        for path, rule, msg in sorted(items):
            print(f"  {path}  [{rule}]  {msg}")

    emit(fnd.errors, "ERRORS")
    emit(fnd.warnings, "WARNINGS")

    n_files = len(command_files) + (
        len([f for f in os.listdir(agents_dir) if f.endswith(".md")])
        if os.path.isdir(agents_dir) else 0
    )
    print(f"\nwtfms-lint: {n_files} files checked, "
          f"{len(fnd.errors)} error(s), {len(fnd.warnings)} warning(s).")
    return 1 if fnd.errors else 0


if __name__ == "__main__":
    sys.exit(main())
