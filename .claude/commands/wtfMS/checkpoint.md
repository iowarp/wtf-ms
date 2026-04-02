---
name: wtfMS:checkpoint
description: Save, restore, or list research state snapshots
argument-hint: "[save|restore|list] [label]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<execution_context>
@.research/STATE.md
</execution_context>

<objective>
Save or restore full research state as a git-tagged checkpoint. Enables session continuity — save before /clear, restore in next session to resume exactly where you left off.
</objective>

<context>
Subcommand: $ARGUMENTS
- `save [label]` — Create checkpoint (e.g., "after-lit-review", "pre-analysis")
- `restore [tag]` — Restore to a previous checkpoint
- `list` — Show all available checkpoints
</context>

<process>

## 1. Parse Subcommand

Extract subcommand and label from $ARGUMENTS. Default to `save` if empty.

## 2. Execute

### Save

Read current state from STATE.md for the auto-label:
```bash
POSITION=$(grep "Current Task\|Phase" .research/STATE.md 2>/dev/null | head -2)
LABEL="${1:-auto-$(date +%Y%m%d-%H%M)}"
```

```bash
git add .research/
git commit -m "checkpoint: save — $LABEL" --allow-empty
git tag "wtfms-checkpoint-$LABEL"
echo "Checkpoint saved: wtfms-checkpoint-$LABEL"
```

### Restore

If no tag provided:
```bash
git tag -l "wtfms-checkpoint-*" | sort -r
```

Ask user which checkpoint to restore via AskUserQuestion.

```bash
git checkout "wtfms-checkpoint-[tag]" -- .research/
echo "Restored from: wtfms-checkpoint-[tag]"
```

### List

```bash
git tag -l "wtfms-checkpoint-*" | sort -r | while read tag; do
  git log -1 --format="%ai — %s" "$tag"
  echo "  Tag: $tag"
done
```

## 3. Present Result

Show checkpoint tag, timestamp, and what state was captured. For restore: show STATE.md position after restore.

</process>

<offer_next>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WTF-MS ► CHECKPOINT [SAVED|RESTORED] ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tag: wtfms-checkpoint-[label]

Resume with `/wtfMS:progress` after restoring.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</offer_next>

<success_criteria>
- [ ] Save: git tag created, .research/ state captured
- [ ] Restore: .research/ state reverted to checkpoint
- [ ] List: all checkpoints shown with timestamps
</success_criteria>
