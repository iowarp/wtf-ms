---
description: "View and edit wtf-MS project configuration"
---

<clio_execution>
Use read, ls, find and grep for file inspection, write/edit for state changes,
and bash for the shell blocks below. Treat $ARGUMENTS as operator text: parse the
command's documented arguments, validate task numbers as positive decimal
integers, and quote actual values in shell commands. Derive NN with printf '%02d'
from the decimal task number; use `.research/tasks/task-NN/` consistently.
Each bash call starts independently; bind actual N, NN, OUT, FILE or checkpoint
values in the same call that uses them. Do not assume shell variables persist.
Read reference files named in execution_context; @ paths are references to read,
not already-inlined file content. Keep project state in `.research/`.

For a command with researcher questions, check that ask_user is available
before running any process step that writes files.
Use ask_user(action="ask", max_rounds=24, questions=[{header:"...",
question:"...", options:[{label:"..."}]}]) for every question below. Preserve the
question text and choices, fill contextual brackets, and collect the researcher's
free text. Send at most four related question objects per round. Cancellation
stops dependent work. If ask_user is unavailable, stop at the first interview
gate before writes and report that this command needs an interactive session.
Close a completed interview with ask_user(action="complete", summary="...",
decisions=[{key:"research_decision",value:"the actual settled decision"}]);
record only answers actually supplied. Keep unresolved questions pending.

Run git add, git commit or git tag only after bash grep confirms
'"commit_research": *true' in `.research/config.json`; absent/false disables them.
Never run git init. Check existing git status first; preserve unrelated staged
changes and report a blocked/failed optional record honestly.
</clio_execution>

<objective>
Display and optionally update .research/config.json settings.
</objective>

<process>

## 1. Read Config

```bash
mkdir -p .research
[ -f .research/config.json ] || cp "${extensionRoot}/resources/templates/config.json" .research/config.json
cat .research/config.json
```

## 2. Display Current Settings

Show each setting with current value and description:

```
WTF-MS SETTINGS (.research/config.json)
─────────────────────────────────────────
model_profile:   [quality|balanced|budget]
  Reserved preference. Route models with configured Clio targets/profiles;
  the extension does not automatically map this value to a model.

web_search:      [true|false]  (default: true)
  Allow web_fetch of specific researcher-provided URLs for literature work.
  Supplied materials come first. False also selects offline citation checks.

auto_checkpoint: [true|false]  (default: true)
  Save a .research/checkpoints/ archive after each completed task.

commit_research: [true|false]  (default: false)
  Let wtf-MS commands run git add/commit/tag on .research/.
  wtf-MS never runs git init. Off by default, matching wtf-p.

data_dir:        [path]
  Where uploaded data files are stored.
─────────────────────────────────────────
```

## 3. Offer to Edit

Use ask_user:
- header: "Edit Settings?"
- question: "Which setting would you like to change?"
- options: "model_profile" | "web_search" | "auto_checkpoint" | "commit_research" | "No changes"

Update config.json with the new value and read it back. For an optional record:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/config.json && git commit -m "research: update settings"
```

</process>

<success_criteria>
- [ ] Current settings displayed with descriptions
- [ ] Changes written to config.json
- [ ] Committed only if commit_research is true
</success_criteria>
