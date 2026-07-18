# 1Step — Product Constitution v1.0

> **This document is the source of truth for the entire product.**
> When implementation conflicts with this document, **this document wins.**
> Do not invent business rules. Do not simplify behavioral logic. If a
> requirement is unclear, propose an improvement — never assume.

## Mission

1Step exists to help people build a healthier, happier and more meaningful life through one small action every day.

This is not a habit tracker.
This is not a fitness application.
This is not a calorie counter.
This is not a productivity application.

It is a **behavioral transformation platform**.

Everything inside the product must reinforce this mission.

---

## Core Philosophy

People rarely fail because they don't know what to do. They fail because change is overwhelming.

1Step removes overwhelm. The application always asks only one question:

> "What is the next smallest action this person can realistically take today?"

The application should **never** create guilt, shame, punishment, comparison, or fear.

Instead it should: **encourage · educate · simplify · support · adapt.**

The user should finish every session feeling: *"I did something good for myself today."*

---

## Product Vision

The application should eventually become an **AI-powered life companion** that understands:
health · nutrition · movement · sleep · stress · mindset · habits · relationships · organization · recovery.

The AI continuously learns which interventions create **sustainable behavioral change**.

---

## Design Philosophy

Minimal · Warm · Human · Calm · Nature-inspired.

No dashboards full of numbers. No points-based gamification. No badges. No leaderboards.

Instead: **progress · reflection · growth · calmness · clarity.**

---

## The Living Tree

The user's journey is a **living procedural tree** — not decoration, but the visual representation of personal growth.

The tree grows **only through real behavior** — not through time, not through button presses, not through streaks.

It must feel alive: it grows, moves, breathes, changes with seasons; it has roots, branches, leaves, flowers, birds, dormancy, recovery. Every tree is **unique**, generated from a deterministic seed. No two users have identical trees.

---

## Behavioral Operating System

The application is a pipeline of **independent engines**, each with a single responsibility. **Never mix business rules between engines.**

```
Behavior Engine → Knowledge Engine → Verification Engine → Level Engine
   → Recovery Engine → Tree Engine → AI Planning Engine
```

- **Behavior Engine** — 20 levels; 14 days min per level; core habits; growth missions; habit progression; difficulty scaling; mastery; consistency; behavioral adaptation.
- **Knowledge Engine** — hundreds of atomic actions. Every action carries metadata: title, why, verification, difficulty, category, contraindications, duration, scaling, weather adaptations, alternatives. **No action without metadata.**
- **Verification Engine** — verify whenever technically possible. Hierarchy: Sensor → Wearables → HealthKit → Google Fit → Health Connect → GPS → AI photo → Timer → Manual. Self-report is the **last** option. Never blindly trust user input when objective verification is possible.
- **Level Engine** — levels are earned through **habit mastery**, never unlocked by time. Dimensions: consistency, core habits, verified actions, stability, mastery score. **Failure does not exist** — if mastery is insufficient, **extend** the level; never reset progress.
- **Recovery Engine** — missing a day / month / year is normal. Never say "You lost your progress." Instead reduce workload, restore momentum, rebuild habits. Recovery is part of the journey.
- **Tree Engine** — the tree **never dies**. Active → growth; inactive → slower growth; long inactivity → dormancy; return → renewal.
- **AI Planner** — every morning generates: today's One Step, three concrete actions, one optional mission, one explanation, one reflection question. Considers: current level, age, medical limitations, weather, season, history, wearables, completion history, recovery state, habit stability, tree state.

---

## Product Principles

Never overwhelm · Never punish · Never shame · Always explain WHY · Always adapt · Always reduce friction · Always favor **consistency over intensity** · Always think long-term.

---

## Development Principles

- This document is the source of truth. **When implementation conflicts with documentation, documentation wins.**
- Do **not** invent business rules. Do **not** simplify behavioral logic.
- If requirements are unclear, **propose improvements instead of assumptions.**
- Every implementation must reinforce the mission of 1Step. Every line of code should help people become healthier one small step at a time.
