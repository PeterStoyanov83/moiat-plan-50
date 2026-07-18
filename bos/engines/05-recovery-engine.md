# 5 — Recovery Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **handle absence and return gently.** It does not fade the tree's leaves (Tree Engine
> reads the same inactivity signal) or evaluate mastery (Level Engine).

## Responsibility
Make disappearing and returning **safe**. Recovery is part of the journey.

## Rules (binding)
- Missing a **day / month / year is normal.** Never say "You lost your progress."
- On return: **reduce workload · restore momentum · rebuild habits** — never reset.
- **Core habits are kept.** Only difficulty and missions change.

## Behavior
- Compute `days_since_last_verified_action`.
- On return after long inactivity (≥14 days), open a **7-day recovery window**
  (`UserProgram.recovery_until = today + 7`).
- During recovery, **scale targets down** (e.g. 8000 → 3000 steps) to restore momentum.

## Current implementation
- `plans/tree_state.py`: `last_activity_date()`, `in_recovery()`, and the recovery-window
  open in `compute_tree_state()` (≥14 idle days → `recovery_until`).
- `UserProgram.recovery_until` field.
- **Gap:** recovery does **not yet reduce action targets** — `daily.py` should apply a
  recovery multiplier when `in_recovery` is true.

## Boundaries (do NOT do here)
- Leaf fade / dormancy visuals → Tree Engine (both read the same inactivity days).
- Mastery math → Level Engine.

## Open / next
- Apply the recovery target multiplier in `daily.today_actions()`.
- Gentle "welcome back" copy on return; taper back to full targets over the 7 days.
