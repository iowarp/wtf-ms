# eval — per-step cost/usage harness

Measures what each step of the wtf-MS research process costs to run. A **step**
is one command (`identify-research`, `literature-review`, …) executed headless
(`claude -p`); the hard-countable numbers from its JSON result — dollars, the
four token axes (input, output, cache-read, cache-write), turns, wall-clock,
web-search calls — are recorded,
aggregated over repeated runs, and checked against a stored baseline. When a
change makes a step more expensive, the baseline check says so.

The research process is a pipeline of these steps — a DAG, since question steps
can loop back to `identify-research` — so you measure it one step at a time and
assemble a per-step cost profile. A step is a single command, not a branch
point; there is nothing to choose between.

There is no quality scoring, by design. An LLM judging the output of another LLM
is no more trustworthy than the run it is judging, so the harness sticks to
numbers it can count exactly.

## What runs where

Split along the line that matters: money. `run_eval.py` is the only piece that
spends — it shells out to `claude`, never runs in CI, and prints a plan without
spending unless you pass `--live`. `metrics.py`, `report.py`, and `baseline.py`
are pure: they parse, aggregate, render, and compare recorded JSON with no
network or subprocess calls, and the tests under `tests/` cover them in CI on
every push.

## Running a step

Start with a dry plan — no spend, and it validates the step file:

```
python3 eval/run_eval.py eval/steps/literature-review.json
```

When the plan looks right, run it for real:

```
python3 eval/run_eval.py eval/steps/literature-review.json --live
```

This writes `eval/results/<timestamp>.json` (gitignored) plus the raw stdout of
every call. Render it:

```
python3 eval/report.py eval/results/<timestamp>.json
```

If a session-limit 429 interrupts the run, the finished reps are already on
disk. Continue once the limit resets:

```
python3 eval/run_eval.py eval/steps/literature-review.json --live --resume-run <timestamp>
```

Per-call and whole-run dollar ceilings (`--max-usd`, `--max-total-usd`) bound
the spend; a transient timeout or non-JSON reply is retried with backoff, while
a 429 aborts the run rather than burning the remaining reps on a wall.

## Steps

A step is a JSON file under `steps/`. It names the command to measure, where its
input state comes from, and (optionally) which cheap checks to price.

```
name       step id (also the baseline filename)
model      default model; overridable with --model
reps       runs of the command
session    "fresh" | "resume-fork"                 resume-fork carries a seed's context
state      {reset: "backup", paths: [".research"]}
fixture    "eval/fixtures/state/<name>"            frozen input, laid down before each rep
seed       {command, prompt, timeout, artifact}    OR a live upstream, run once
measure    {command, prompt, timeout, artifact}    the command this step measures
checks     [{name, disable_suffix}]                optional; priced with --price-checks
```

Give a step exactly one input source: a `fixture` (a committed state directory
under `fixtures/state/`), a `seed` (a live upstream command run once), or
neither (the first step, `identify-research`, starts from an empty workspace).
`resume-fork` needs a seed to fork from.

`state.reset` is `"backup"`, not git: `.research/` is untracked runtime state,
so the runner copies the declared paths aside before it touches them and
restores them on exit. Restoring via `git` would delete untracked state, not
recover it.

### Isolated inputs (fixtures)

`literature-review.json` measures its command from a frozen post-identify
`.research` state (`fixtures/state/after-identify/`), laid down fresh before
every rep. No live upstream means no compounding variance, and re-baselining one
step costs a few cents.

The tradeoff: a fixture step runs in a **fresh** session (a conversation can't
be committed to disk, only file-state can), so it measures the command's
*marginal* cost with its input held constant — not the carry-path cost of the
real workflow, where each step inherits the previous one's context and warm
cache. That isolation is what keeps the per-step numbers clean to compare over
time; it also means the absolute figures run lower than a real end-to-end study.

The pipeline is `identify-research → literature-review → define-virtual-lab →
define-research-tasks → execute-task` (literature-review can loop back to
identify-research). Each step reads the state the previous ones wrote, so its
fixture is the frozen output of the step before it.

Bootstrap the fixture chain once with a forward run: `--save-fixture <name>`
freezes a step's output into `fixtures/state/<name>/` after its baseline reps,
which becomes the next step's input. Walk the pipeline in order, committing each
fixture, and you can then baseline every step in isolation. Refresh the
fixtures when a command's output format changes.

## Checks

The guardrails a command runs (e.g. `verify_citations` on the literature review)
are cheap optional checks, included in the step's normal measured cost. To find
what one adds, list it under `checks` with a `disable_suffix` that tells the run
to skip it, and pass `--price-checks`: the runner re-runs the step with the
check disabled and reports the difference as that check's increment. It's an
add-on to the step, not a separate run to compare against.

```
python3 eval/run_eval.py eval/steps/literature-review.json --live --price-checks
```

## Baselines

A baseline is a step's expected cost/usage, blessed from a real run:

```
python3 eval/baseline.py eval/results/<timestamp>.json --update
```

That writes `eval/baselines/<step>.json` — committed, so it's the public record
of what the step costs. Later runs check against it:

```
python3 eval/baseline.py eval/results/<new-run>.json
```

Because runs are non-deterministic, comparison is mean-vs-mean. A metric that
moved more than the **band** — a fixed percentage (default 20%) stored in the
baseline file — is flagged as notable, in either direction. This is
observability, not a gate: the comparison always exits 0 and records what
changed so you can respond, rather than failing the run. `--all` shows every
metric, not just the notable moves.

A fixed percentage beats a multiple of the measured spread here: three reps is
too few for a stdev to trust, and a number written plainly in the file is easy
to read and to widen for a genuinely jumpy metric.

## Per-model cost

A step's cost is also split by model in the report (`total_cost_usd` is the
sum). This is where a subagent on a different model shows up — the committed
literature-review baseline (~$0.98) split as `sonnet ~$0.78 + haiku ~$0.20`. The
top-level token axes are orchestrator-only, so the per-model split is the only
place the subagent's tokens surface. The regression band stays on the complete
`total_cost_usd`.

## Adding a step

Multi-line prompts need valid JSON escaping, so generate the file rather than
hand-editing quotes. The files in `steps/` were written by a short Python script
that assembles the dict and `json.dump`s it; copy that approach. Run the dry
plan first to confirm it validates, then `--live`.
