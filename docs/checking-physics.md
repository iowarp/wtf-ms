# Physical sanity checks

After fabricated citations, the next class of "plausible but wrong" LLM output
is **physically impossible numbers** — a temperature below absolute zero, a
negative density, a porosity of 120%, an alloy whose composition doesn't sum to
100%. `wtf-ms/scripts/check_physics.py` scans a task's generated outputs
and flags these before they get committed to your research state.

## What it checks

| Rule | Severity | Example caught |
|------|----------|----------------|
| `temp-kelvin` / `temp-celsius` / `temp-fahrenheit` | error | `-5 K`, `-300 °C` (below absolute zero) |
| `density` | error / warn | `-2.1 g/cm³`, `0 g/cm³` (error); `45 g/cm³` (warn — exceeds any known solid) |
| `fraction` | error | `Cr 105 wt%`, `porosity 120%` (outside 0–100%) |
| `composition` | warn | `Fe 70 wt%, Cr 18 wt%, Ni 9 wt%` sums to 97%, not ~100% |

It exits non-zero if any **error** (physical impossibility) is present.

## Keeping false positives low

v1 only asserts what is unconditionally true. It does not flag a value just
for being negative, because many materials-science quantities are legitimately
negative and must pass silently:

- DFT total and formation energies (`-8.35 eV/atom`, `-45 kJ/mol`)
- compressive stresses (`-250 MPa`)
- thermal-expansion mismatches, coordinates, gauge pressures

Only quantities that are non-negative by definition — absolute temperature,
density, a bounded fraction — are sign-checked. Two further cases are handled
so they don't misfire:

- A temperature *unit* also appears in signed quantities — differences (`ΔT =
  -5 K`), rates (`-50 K/s`), and gradients (`-12 K/mm`) — so a negative value
  is only flagged when it reads as an absolute temperature.
- A bounded `%` in a relative-change context (`efficiency improved by 250%`) is
  not flagged, since a relative change can exceed 100%.

Ranges written with an en-dash (`250–300 W`) or hyphen (`5-10 µm`) are not
misread as negative numbers.

This behavior is pinned by `tests/test_check_physics.py` (run in CI); the
cases that matter most are the negative ones — valid values, including
legitimately-negative ones, that must produce zero findings.

## When it runs

`/wtfMS:execute-task` runs it on a completed task's outputs (all task types) as
an **advisory** step before committing — fix `IMPOSSIBLE` errors, review
`IMPLAUSIBLE` warnings with the user. It never hard-blocks.

## Running it manually

```bash
python3 wtf-ms/scripts/check_physics.py .research/tasks/task-01/*.md
python3 wtf-ms/scripts/check_physics.py --json protocol.md
```

Zero dependencies (Python stdlib only).

## Limitations

- It checks values in isolation against absolute physical bounds; it does not
  check whether a value is *reasonable for a specific material or method*
  (e.g. a 5000 K anneal of a polymer is not caught — 5000 K is a valid
  temperature). Domain-specific range checks are a possible future extension.
- Unit coverage is a curated set (temperature, density, fractions). Values in
  units outside that set pass unchecked.
