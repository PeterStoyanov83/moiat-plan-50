# 4 — Level Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **evaluate mastery and decide promote-or-extend.** It never selects actions, verifies
> them, or renders the tree.

## Responsibility
Move users through the 20 levels **by mastery, never by time**. Guarantee that
**failure does not exist**.

## Rules (binding)
- Levels are **earned**, not unlocked by elapsed time.
- Evaluation dimensions: **consistency · core habits · verified actions · stability ·
  mastery score.**
- **If mastery is insufficient → extend the level (+7 days). Never reset progress.**
- Never surface "failed" / "lost". Extension message is encouraging:
  *"Твоите корени укрепват. Нека им дадем още малко време."*

## Scoring
- **Mastery weights:** consistency `.40` · verified actions `.30` · core-habit stability
  `.20` · growth missions `.10`.
- **Requirement bands** (consistency % / completion % / core-habit %):
  L1–5 `80/70/75` · L6–10 `80/75/80` · L11–15 `85/80/85` · L16–20 `90/85/90`.
- Promote only after `min_days + extended_days` elapsed **and** all three band thresholds met.

## Current implementation
- `plans/progression.py`: `scores_for_period()`, `mastery_score()`, `evaluate_level()`
  → returns `{decision: in_progress|promote|extend, scores, mastery, level, message}`
  and mutates `UserProgram`. Called on each completion in `views.step_done`.
- Bands seeded in `Level` (`migrations/0008`).

## Boundaries (do NOT do here)
- Deciding an action counts → Verification Engine (reads `ActionLog.status`).
- Reducing workload after a gap → Recovery Engine.

## Open / next
- Scheduled nightly re-evaluation (not only on completion) so extensions apply even when idle.
- Per-level promotion celebration event routed to the Tree Engine (`setLevel` + blossom).
- Surface promote/extend messages in the UI.
