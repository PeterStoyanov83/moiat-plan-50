# PROJECT_CONTEXT — 1Step

**1Step („Една стъпка")** is a **behavioral transformation platform**: it helps people
build a healthier, happier, more meaningful life through **one small verified action a
day**, visualized as a **living tree** that grows only from real behavior.

It is NOT a habit tracker, fitness app, calorie counter, or productivity app.

## Read these before building (in order)
1. **[bos/CONSTITUTION.md](bos/CONSTITUTION.md)** — the source of truth. If code and docs
   disagree, **the docs win.** Never invent business/progression/verification rules.
2. **[bos/README.md](bos/README.md)** — the engine pipeline + non-negotiables.
3. The **engine spec** for whatever you're touching — [bos/engines/](bos/engines/):
   Behavior · Knowledge · Verification · Level · Recovery · Tree · AI Planner.
4. **[bos/STATUS.md](bos/STATUS.md)** — current implementation state (extend, don't duplicate).

## Non-negotiables (never violate)
- Never guilt, shame, punish, compare, or use fear. Always explain **WHY**.
- The tree grows **only from real, verified behavior** — never time, presses, or streaks.
- Levels are **earned by mastery**, never unlocked by time. **Failure does not exist** —
  extend, never reset.
- **Every action has metadata.** Prefer **consistency over intensity**. Think long-term.

## Tech at a glance
- Django app `plans` (package `onestep`), Postgres on Railway, local sqlite for dev.
- BOS engines → code: `models.py` · `daily.py` · `verification.py` · `progression.py` ·
  `tree_state.py` · `static/plans/tree-engine.js` (vendored, used as-is) · `ai_companion.py`.
- Run tests: `python manage.py test plans`. Full technical state: [HANDOFF.md](HANDOFF.md).

## Working rule (from [CLAUDE.md](CLAUDE.md))
If implementation reveals a design weakness, **do not silently fix it** — explain, propose
improvements, and wait for approval. Think like a product architect, behavioral
psychologist, senior engineer, and UX designer at once.
