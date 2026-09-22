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
[ -f .research/config.json ] || cp ${CLAUDE_PLUGIN_ROOT}/wtf-ms/templates/config.json .research/config.json
cat .research/config.json
```

## 2. Display Current Settings

Show each setting with current value and description:

```
WTF-MS SETTINGS (.research/config.json)
─────────────────────────────────────────
model_profile:   [quality|balanced|budget]
  Controls agent model tier. balanced = default.

web_search:      [true|false]  (default: true)
  Allow agents to search the web during literature review and
  literature tasks. Supplied papers are always used first.

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

Use AskUserQuestion:
- header: "Edit Settings?"
- question: "Which setting would you like to change?"
- options: "model_profile" | "web_search" | "auto_checkpoint" | "commit_research" | "No changes"

Update config.json with the new value. Commit only if commit_research is true.

</process>

<success_criteria>
- [ ] Current settings displayed with descriptions
- [ ] Changes written to config.json
- [ ] Committed only if commit_research is true
</success_criteria>
