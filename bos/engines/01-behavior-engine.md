# 1 — Behavior Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> the **structure of the journey** — levels, habit types, difficulty scaling. It does
> NOT decide if an action happened (Verification), whether to promote (Level), or how
> the tree looks (Tree).

## Responsibility
Own the program's shape: 20 levels, ≥14 days each; the split between **Core Habits**
(permanent lifestyle foundations) and **Growth Missions** (temporary variety); and how
an action's difficulty **scales with level**.

## Rules (binding)
- **20 levels.** Minimum **14 days** per level.
- Each level **builds on** the previous. The user does not advance just because 14 days
  passed — advancement is the Level Engine's call, on mastery.
- **Every day contains ≥3 actions.** Core habits remain day to day; missions rotate for
  variety.
- **Difficulty scales by level**, per each action's `level_scaling` (e.g. walk: 2000 →
  10 000 steps across L1→L20). Favor **consistency over intensity**.

## Contracts
- `Level(number, min_days, consistency_req, completion_req, core_habit_req)` — static config.
- `UserProgram(response, current_level, level_started_on, extended_days, recovery_until)` —
  the user's position. **`current_level` is system-owned; never a user input.**
- `ActionDef.type ∈ {core_habit, growth_mission}`; `ActionDef.level_scaling` → target per level.

## Current implementation
- `plans/models.py`: `Level`, `UserProgram`, `ActionDef` (+ `target_for_level`). Seeded 1–20 in `migrations/0008`.
- `plans/daily.py::today_actions()` — serves ≥3 actions (core first, then a mission), level-scaled titles.
- **Home-screen area choice (UX layer):** the ritual now opens on **category bubbles**
  (`daily.categories_meta()`); the user picks an area and `today_actions(category=…)` serves only
  that area's actions. Selection rules are unchanged (core-first, weakest-habit adaptation, safety
  gating) — they now run *within* the chosen area. Note: the "≥3/day includes core habits" guarantee
  becomes user-gated (they choose which areas to engage).

## Boundaries (do NOT do here)
- Verifying completion → Verification Engine.
- Promotion/extension math → Level Engine.
- Inactivity handling → Recovery Engine.

## Open / next
- Expand the level bands with per-level mission themes / difficulty curves.
- Behavioral adaptation (bias action selection toward the user's weakest habits).
