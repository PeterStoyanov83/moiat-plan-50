# 7 — AI Planner Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **compose the daily plan.** It orchestrates the other engines' outputs into one calm,
> personalized morning — it does not redefine their rules.

## Responsibility
Every morning, generate the user's day in a way that removes overwhelm and always
explains WHY.

## Rules (binding)
The morning generation produces exactly:
- **Today's One Step** (the single smallest realistic action),
- **Three concrete actions**,
- **One optional mission**,
- **One explanation** (the WHY),
- **One reflection question**.

Tone is warm, calm, human. **Never overwhelm, never shame.** Prefer consistency over intensity.

## Inputs considered
current level · age · medical limitations (contraindications) · weather · season ·
history · wearables · completion history · recovery state · habit stability · tree state.

## Current implementation
- `plans/ai_companion.py` — Claude (Haiku) picks a step + writes a warm line; **falls back
  to rule-based** when the API/key is absent.
- `plans/daily.py::today_actions()` — the rule-based 3-action selection (core first + a
  mission), level-scaled, each with its `why`. Rendered in `ritual.html` (task + why).
- **Gap vs spec:** does not yet incorporate weather, contraindications, habit stability,
  or emit a **reflection question**; "one optional mission" is not yet distinct from the 3.

## Boundaries (do NOT do here)
- Difficulty scaling → Behavior. Verification → Verification. Promotion → Level.
- The planner **reads** those outputs; it must not reimplement them.

## Open / next
- `/api/today` producing the full morning payload (one step + 3 actions + mission +
  explanation + reflection question).
- Feed weather/season + `contraindications` + `HabitStability` into selection.
- Persist the reflection answer (storage decision) for the AI to learn from.
