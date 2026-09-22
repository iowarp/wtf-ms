---
description: "Save, restore, or list research state snapshots"
argument-hint: "[save|restore|list] [label]"
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

<execution_context>
@.research/STATE.md
</execution_context>

<objective>
Save or restore full research state as a snapshot archive under `.research/checkpoints/`. Enables session continuity — save before ending the session, restore in the next session to resume exactly where you left off. Works with or without git; when `commit_research` is true in config.json, a git tag is added as well.
</objective>

<context>
Subcommand: $ARGUMENTS
- `save [label]` — Create checkpoint (e.g., "after-lit-review", "pre-analysis")
- `restore [name]` — Restore a previous checkpoint
- `list` — Show all available checkpoints
</context>

<process>

## 1. Parse Subcommand

Extract subcommand and label from $ARGUMENTS. Default to `save` if empty.

## 2. Execute

### Save

```bash
mkdir -p .research/checkpoints
POSITION=$(grep -i "current task\|phase" .research/STATE.md 2>/dev/null | head -2 | tr '\n' ' ')
LABEL="${1:-auto}"
NAME="$(date +%Y%m%d-%H%M)-$LABEL"
tar czf ".research/checkpoints/$NAME.tgz" --exclude='./data' --exclude='./checkpoints' -C .research .
ls -la ".research/checkpoints/$NAME.tgz" && echo "Checkpoint saved: $NAME ($POSITION)"
```

The archive holds every state file and all task outputs. Registered data under `.research/data/` is excluded; it is the researcher's, and it is never overwritten by a restore.

If `commit_research` is true, also tag:
```bash
grep -q '"commit_research": *true' .research/config.json 2>/dev/null && git add .research/ && git commit -m "checkpoint: save — $LABEL" --allow-empty && git tag "wtfms-checkpoint-$LABEL"
```

### Restore

If no name provided:
```bash
ls -1t .research/checkpoints/*.tgz 2>/dev/null
```
Ask the user which checkpoint to restore via ask_user. Confirm: restoring overwrites the current state files and task outputs (not `data/`).

```bash
tar tzf ".research/checkpoints/[name].tgz" | head -20
tar xzf ".research/checkpoints/[name].tgz" -C .research
grep -i "current task\|phase" .research/STATE.md | head -2
echo "Restored from: [name]"
```

### List

```bash
ls -1t .research/checkpoints/*.tgz 2>/dev/null | while read f; do
  echo "$(date -r "$f" '+%Y-%m-%d %H:%M')  $(basename "$f" .tgz)  $(du -h "$f" | cut -f1)"
done
git tag -l "wtfms-checkpoint-*" 2>/dev/null | sort -r
```

## 3. Present Result

Show checkpoint name, timestamp, and what state was captured. For restore: show the STATE.md position after restore.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► CHECKPOINT [SAVED|RESTORED] ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Checkpoint: .research/checkpoints/[name].tgz

Resume with `/wtfMS:progress` after restoring.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</offer_next>

<success_criteria>
- [ ] Save: archive created under .research/checkpoints/, data/ excluded
- [ ] Restore: state reverted from the chosen archive after confirmation
- [ ] List: all checkpoints shown with timestamps and sizes
- [ ] Git tag only when commit_research is true
</success_criteria>
