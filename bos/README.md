# 1Step BOS — Behavioral Operating System

This directory is the **governing file system** for building 1Step. It explains the
product, encodes the rules, and guides every implementation decision. Read it before
you build.

## How to use this (for any agent or developer)

1. **Read [`CONSTITUTION.md`](CONSTITUTION.md) first — always.** It is the source of
   truth. If your change conflicts with it, the Constitution wins; change the plan,
   not the Constitution.
2. **Find the engine you're touching** in [`engines/`](engines/). Each engine has a
   **single responsibility** — never implement another engine's rules inside it.
3. **Check [`STATUS.md`](STATUS.md)** for what's already built and where it lives in
   the codebase, so you extend rather than duplicate.
4. **If a rule is missing or unclear, propose an improvement** (add a note to the
   relevant engine file) — do not silently assume.

## The engine pipeline

```
Behavior → Knowledge → Verification → Level → Recovery → Tree → AI Planner
```

Data flows down the pipeline; **business rules never leak sideways**.

| # | Engine | Single responsibility | Spec |
|---|--------|-----------------------|------|
| 1 | Behavior | Levels, core habits, missions, difficulty scaling | [engines/01-behavior-engine.md](engines/01-behavior-engine.md) |
| 2 | Knowledge | The atomic-action library + full metadata | [engines/02-knowledge-engine.md](engines/02-knowledge-engine.md) |
| 3 | Verification | Prove an action really happened | [engines/03-verification-engine.md](engines/03-verification-engine.md) |
| 4 | Level | Mastery evaluation → promote or extend | [engines/04-level-engine.md](engines/04-level-engine.md) |
| 5 | Recovery | Gentle return after inactivity | [engines/05-recovery-engine.md](engines/05-recovery-engine.md) |
| 6 | Tree | Living visualization of real growth | [engines/06-tree-engine.md](engines/06-tree-engine.md) |
| 7 | AI Planner | The daily plan (one step + 3 actions + reflection) | [engines/07-ai-planner-engine.md](engines/07-ai-planner-engine.md) |

## Non-negotiables (fast reference)

- **Never** guilt, shame, punish, compare, or use fear.
- The tree grows **only from real, verified behavior** — never time, presses, or streaks.
- Levels are **earned by mastery**, never unlocked by time. **Failure does not exist** — extend, never reset.
- **Every action has metadata** (title, why, verification, …). No action without it.
- **Always explain WHY.** Prefer **consistency over intensity**. Reduce friction. Think long-term.
- Verify objectively whenever possible; **self-report is the last resort.**

## App context

1Step is a Django app (`plans`), deployed on Railway. General technical/operational
state lives in [`../HANDOFF.md`](../HANDOFF.md); the original engineering design notes
in [`../design/HABIT_ENGINE_SPEC.md`](../design/HABIT_ENGINE_SPEC.md). This BOS
supersedes those where they disagree.
