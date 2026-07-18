# 6 — Tree Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **visualize real growth.** It renders state supplied by the other engines; it never
> decides mastery, verification, or which actions to serve.

## Responsibility
Be the living, unique visualization of the user's journey. The tree **never dies**.

## Rules (binding)
- The tree grows **only through real, verified behavior** — never time, presses, or streaks.
- It must feel alive: grows, moves, breathes; seasons; roots, branches, leaves, flowers,
  birds, dormancy, recovery.
- **Every tree is unique**, from a deterministic seed. No two users identical.
- Reactions: Active → growth · Inactive → slower growth · Long inactivity → dormancy ·
  Return → renewal. **Wood and roots never regress.**

## Growth events
- **Daily verified action** → a new leaf, up close (zoom-into-leaf reveal). Plays **only
  when the user is looking** at the tree — never before.
- **Level completion** → major growth: new branch, thicker trunk, flowers.
- **Long-term consistency** → birds, fruit, seasonal shifts.

## Contracts (engine is used AS-IS via its public API)
- `mountTree(canvas, { userId(seed), completedActions, level(1..20), season })`.
- `queueActions(total)` / `playReveal()` — action-driven growth, visibility-gated.
- `setLevel(1..20)` (trunk = discipline), `setHealth(0..100)`, `setDormant(bool)`.
- `growthStage(n)` — Bulgarian stage labels.

## Current implementation
- `plans/static/plans/tree-engine.js` — **vendored, used as-is** (only the growth-stage
  labels were localized to Bulgarian). Source demo: `/Users/peterstoyanov/Progress Tree/`.
- `plans/tree_state.py::compute_tree_state()` derives `age(done) · growth_stage · level ·
  health · dormant` and feeds the template.
- `progress.html` mounts at the last-seen count, queues new growth, plays the reveal only
  when on screen; marks "seen" only after the reveal lands.

## Boundaries (do NOT do here)
- Any behavioral rule. The tree is a **pure render** of engine outputs.

## Open / next
- Route level-up + long-term events (branches, flowers, birds) explicitly from Level Engine.
- Reflect recovery renewal visibly on return.
