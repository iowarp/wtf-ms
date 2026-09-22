# WTF-MS for Clio Coder

WTF-MS turns a materials-science research direction into a confirmed question,
a literature map, a realistic resource inventory, an executable task plan, and
an author-reviewed wtf-p handoff. This is the hand-written Clio port of Daisy
Quach's Claude implementation. The package requires Clio Coder 0.4.6 or later.

## Install and invoke

From the wtf-ms repository root:

```bash
clio-coder extensions discover ./clio --json
clio-coder extensions install ./clio --user
```

In an existing Clio session, run `/resources extensions reload`, or restart it.
Use `--project` instead of `--user` for a project installation. Installation copies
the package and records its content digest; editing this source does not update
an installed copy. Reinstall intentionally when publishing local changes, then
reload. The extension ID is `wtfms`; command spelling is case-sensitive `wtfMS`:

```text
/wtfMS:identify-research
/wtfMS:literature-review
/wtfMS:define-virtual-lab
/wtfMS:define-research-tasks
/wtfMS:execute-task 1
/wtfMS:wtfp
```

The relative prompt paths produce those names. There are no flat aliases.

## Research loop and commands

Identify research → review literature → define the virtual lab → define research
tasks → execute tasks → bridge to wtf-p. A literature finding can send the
researcher back to revise the question. Every interview belongs to the interactive
orchestrator; agents synthesize/write and return checkpoints for it to resolve.
The orchestrator reads written files back before claiming completion.

| Command | Use |
| --- | --- |
| `/wtfMS:identify-research` | Interview, compare three candidates, confirm selection and scope |
| `/wtfMS:literature-review` | Review supplied material and provided URLs; decide citation/keyword changes |
| `/wtfMS:define-virtual-lab` | Map equipment, compute, licenses, collaborators and resource gaps |
| `/wtfMS:define-research-tasks` | Choose/customize a workflow, interview assumptions, decide flags/defaults |
| `/wtfMS:execute-task [N\|all]` | Confirm and execute tasks, inspect files, review advisory findings |
| `/wtfMS:wtfp` | Choose paper scope and author decisions, preview a gated paper handoff |
| `/wtfMS:add-task` | Add a task and its numbered directory |
| `/wtfMS:remove-task N` | Confirm removal and reconcile dependencies |
| `/wtfMS:archive-task N` | Preserve a task outside the active workflow |
| `/wtfMS:upload-data [path]` | Register supplied files, optionally copy them |
| `/wtfMS:status` | Inspect the research dashboard |
| `/wtfMS:progress` | Inspect progress and choose the next action |
| `/wtfMS:checkpoint [save\|restore\|list] [label]` | Save or restore state archives |
| `/wtfMS:pause-research` | Pause and save a checkpoint |
| `/wtfMS:resume-research` | Restore active state and show the next task |
| `/wtfMS:settings` | Inspect/change project settings |
| `/wtfMS:help` | Show the command reference |

State lives in `.research/`: RESEARCH.md, LITERATURE.md, VIRTUAL-LAB.md,
WORKFLOW.md, STATE.md, DATA-INDEX.md and config.json. Tasks use
`.research/tasks/task-NN/`, with NN derived by `printf '%02d'`. Supplied data,
checkpoints and wtf-p handoffs live in their corresponding subdirectories.
The default config is copied verbatim from resources/templates/config.json when
identify-research initializes missing configuration.

## Host behavior and limits

Clio has no web search tool. Literature work starts with `.research/data/` and
DATA-INDEX.md, then uses `web_fetch` only for specific researcher-provided URLs.
Sources Reviewed records actual coverage and inspection depth. Unreadable PDFs
require usable text; listing a paper is not reading it. `web_search: false`
disables provided-URL fetching and selects `verify_citations.py --offline`, so
citation checks do not bypass the researcher's network choice. Crossref checks
when enabled verify identities; they do not expand the literature corpus.

`ask_user` requires an interactive Clio session and is unavailable in headless
runs. These prompts stop/refuse an interview gate when it is unavailable; the
host does not synthesize default answers. Read-only help/status can still work
without an interview. A headless fleet requires already-confirmed input and must
return a checkpoint when another answer is needed. Fresh dispatches receive the
full relevant context; the extension does not assume a resumable worker transcript.

Agent recipes bind only their own extension skills. Required tools include read,
context, and write/edit for writers. The executor optionally exposes bash and
web_fetch; the reviewer optionally exposes web_fetch. Host policy and runtime
availability still determine which tools a worker actually gets. An external
worker that lacks canonical skill/context tools cannot be treated as equivalent
to a native Clio worker. `model_profile` in research config is a reserved preference;
choose actual models through Clio's configured targets/profiles.

The three shipped Python scripts are byte-for-byte copies of the canonical
stdlib-only checkers. Run applicable checks through the prompt's bash blocks;
if python3 is missing, skip silently. Physics findings, citation matches and
script issues are advisory. The researcher decides corrections/removals; warnings
and accepted exceptions remain documented. Offline citation checks cannot resolve
Crossref identities. File arguments must exist: the checkers do not recursively
scan directory arguments, and unreadable files can warn without failing the process.
Generated scripts/protocols do not establish that simulations or experiments ran.

## Fleet usage

The primary execution path is `/wtfMS:execute-task`, which owns task confirmation,
readback, advisory checks, researcher decisions, state updates and checkpoints.
The optional v4 fleet is only execute → readonly verify. Both recipes are shipped.
Its write boundary is `.research/tasks/`; the selected task subdirectory is also
an instruction, not a dynamically narrowed host boundary. The fleet never grants
writes to LITERATURE.md; proposed global updates are returned for its caller.

After the task and assumptions are confirmed, a caller can use:

```bash
clio-coder fleet run wtfms-execute-task --var task=task-01 --var 'approval=Task 01 and its documented assumptions are researcher-approved.' --var 'retrieval=web_search=false; supplied materials only; no URLs authorized.'
```

Replace those values with actual approved state. The caller checks receipts,
status prefixes and files, handles any needs_input/task_blocked return, and only
then runs advisory checks and reconciles WORKFLOW.md/STATE.md. No fleet execution
was performed during package validation.

### Registered code-step example

Clio supports `kind: code`, but its command field is a project registry ID, not a
shell command. The default fleet omits a physics code step: its nonzero exit could
stop a fleet before the researcher decides an advisory finding. The prompt-driven
path preserves advisory behavior and needs no registry.

For a separately authored project code step, declare an explicit argv in
`.clio-coder/fleets/commands.yaml`. Example for a project that has this `clio/`
source directory and these actual task files:

```yaml
version: 1
commands:
  wtfms-check-physics:
    argv:
      - python3
      - clio/resources/scripts/check_physics.py
      - .research/tasks/task-01/task-01-SUMMARY.md
      - .research/tasks/task-01/task-01-model.md
    timeoutMs: 60000
    description: Physical sanity scan of the explicitly listed task-01 files
```

An optional project fleet step could name `command: wtfms-check-physics`,
`kind: code`, `scope: readonly`, and `dependencies: [verify]`. Adapt the argv to
the actual task outputs before each run. For a copied user installation, replace
the script argument with its actual installed absolute path. The registry does
not expand extensionRoot, shell globs, or fleet `{{task}}` variables; v4 code
steps do not accept an arbitrary task-directory argument. Missing registries
produce setup diagnostics. A direct physics step fails on impossible values;
do not use that as an automatic deletion or scientific rejection policy.

## Install wtf-p alongside WTF-MS

For the RC2 adapter this handoff targets, the researcher can run:

```bash
npx --yes --package=wtf-p@0.6.0-rc.2 -- wtf-p install clio
```

This is a suggested operator command; the bridge does not execute it. Invoke
`/wtfMS:wtfp` inside Clio after activating the installed source in the host.
Detection reports **source present, activation unverified** rather than assuming
that files are enabled in the current session.

The bridge inspects both Claude roots independently: a non-blank
`CLAUDE_CONFIG_DIR` with leading `~` expanded (otherwise `~/.claude`), and the
project `.claude/`. It parses every modern plugin.json name/version, checks the
modern commands, and records legacy trees too. Malformed, incomplete, unexpected
or mixed-generation results route to the handoff. A matching `wtfp` name and
`0.6.0-rc.2` version identify RC2 source; other versions have unverified
compatibility. Nothing is removed.

The Clio source check uses non-blank `CLIO_CODER_CONFIG_DIR` with leading `~`
expanded, otherwise `~/.config/clio-coder`, and reads
`extensions/wtf-p/` (wtf-p's own installer) or `extensions/wtfp/` (Clio's native `extensions install`, which uses the manifest id). The bridge checks both; the directory is not
`wtfp`. Preserve whitespace inside configured paths. A Clio manifest selects the
modern/uncertain handoff path, even if a legacy Claude command tree also exists.

Existing 0.6 state takes precedence over source detection: project.json, a
config.json with a wtfp.project schema, state.json, decisions.json,
structure/outline.json, sources/ or evidence/ under `.planning/` disables the
legacy writer and new-paper. In that case 01-new-paper.md carries a
`/wtfp:progress` inspection-and-reuse brief. Paste that first inside Clio;
map-project (02) is the first write after confirming existing state. Incomplete
or invalid records call for inspection/repair, never reinitialization.

For a new project, paste 01 into `/wtfp:new-paper` inside Clio, followed by
`/wtfp:map-project` and `/wtfp:create-outline`. The author confirms each gate.
Handoffs authorize only selected hidden/ignored materials and retain exclusions.
Missing typed facts are omitted and listed under Not supplied; full config keys,
locked/deferred decisions and the completed/planned boundary are preserved.
Deferred decisions stay outside active work until explicitly resolved. Sources
and evidence use stable record URIs, schema kinds and identity-based deduplication;
a shared citation key is a collision to report, not proof of identity. Crossref
identity checking is not full-text inspection or scientific support.

The legacy 0.5 writer is reachable only for an unambiguous legacy-only detection
with no 0.6 records. It preserves an existing config.json. Optional git recording
requires commit_research=true and stages only the four named handoff files, or
the legacy PROJECT.md/config.json files actually written, never `.planning/` as
a directory. Unrelated staged changes block the optional record.

## Git policy

WTF-MS never runs `git init`. By default `commit_research` is false and research
commands do not stage, commit or tag. Each optional recording action first checks
`.research/config.json` with bash grep for `"commit_research": true`. Set that
value deliberately in `/wtfMS:settings` to enable recording in an existing git
worktree. Preserve unrelated staged changes. Checkpoint archives work without git.
The installation/build/validation of this package performs no commits.

## Provenance and validation

Canonical content is `commands/`, `agents/`, and
`wtf-ms/` in this repository. References/templates are copied verbatim into
resources and relevant skill references; scripts are copied without modification.
The exception is `record_metrics.py`, which collects token usage from Claude Code
`Stop` hooks and has no Clio equivalent, so the extension does not ship it.
The 0.6 handoff payload blocks remain verbatim. The task verifier is a Clio support
recipe. The executor is ported from the restored canonical file. See NOTES.md for
production-loader checks, guardrail smoke checks and complete discover output.
