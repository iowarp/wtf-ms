---
version: 4
name: wtfms-execute-task
description: Execute one pre-approved research task and independently inspect its output files.
steps:
  - kind: agent
    id: execute
    agent: wtfms-task-executor
    scope: workspace
    writes: [.research/tasks/]
    dependencies: []
  - kind: agent
    id: verify
    agent: wtfms-task-verifier
    scope: readonly
    dependencies: [execute]
maxWorkers: 1
onFailure: stop
---

Task directory basename: {{task}}. Researcher-approved task and assumptions:
{{approval}}. Researcher-provided URLs and config policy: {{retrieval}}.

The caller validates task as task-NN with two-digit NN (derive with printf %02d),
checks the task exists and dependencies are settled, and supplies confirmed
interview answers before starting. Read the task entry from `.research/WORKFLOW.md`
and use `.research/RESEARCH.md`, relevant literature, VIRTUAL-LAB.md and registered
data. For literature tasks, inspect `.research/data/` and DATA-INDEX.md first.
Write only in `.research/tasks/{{task}}/`; the fleet's tasks/ allowlist is the
maximum boundary, not authorization to edit other tasks. Put proposed global
literature updates in the task summary for the caller to reconcile. The verifier
reads the output inventory and summary before returning its own typed checks.

The caller inspects every receipt and status prefix, then reads outputs back.
Stop at task_blocked: or needs_input:, collect the researcher response outside
the fleet, and start a new run with that answer and complete context. Only the
interactive caller runs the advisory guardrails and presents findings, marks the
workflow task complete, updates STATE.md, checkpoints and optionally records git.
Use `/wtfMS:execute-task` for the complete interactive workflow.
