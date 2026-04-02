---
name: wtfMS:settings
description: View and edit wtf-MS project configuration
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Display and optionally update .research/config.json settings.
</objective>

<process>

## 1. Read Config

```bash
cat .research/config.json 2>/dev/null || echo "No config.json found — will create default."
```

## 2. Display Current Settings

Show each setting with current value and description:

```
WTF-MS SETTINGS (.research/config.json)
─────────────────────────────────────────
model_profile:   [quality|balanced|budget]
  Controls agent model tier. balanced = default.

web_search:      [true|false]
  Allow agents to search the web during literature review.

auto_checkpoint: [true|false]
  Auto-save checkpoint after each completed task.

commit_research: [true|false]
  Include .research/ state in git commits.

data_dir:        [path]
  Where uploaded data files are stored.
─────────────────────────────────────────
```

## 3. Offer to Edit

Use AskUserQuestion:
- header: "Edit Settings?"
- question: "Which setting would you like to change?"
- options: "model_profile" | "web_search" | "auto_checkpoint" | "commit_research" | "No changes"

Update config.json with new value and commit.

</process>

<success_criteria>
- [ ] Current settings displayed with descriptions
- [ ] Changes written to config.json
- [ ] Committed if changed
</success_criteria>
