# 2 — Knowledge Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> the **library of atomic actions and their metadata**. It does not select the day's
> actions (Behavior/AI Planner) or verify them (Verification).

## Responsibility
Hold **hundreds of atomic actions**, each fully described. The library is the product's
knowledge — warm, safe, and specific.

## Rules (binding)
- **No action exists without metadata.** Every action must carry:
  `title · why · verification · difficulty · category · contraindications · duration ·
  scaling · weather_adaptations · alternatives`.
- **Always explain WHY** — the `why` is shown to the user, never omitted.
- Actions must be safe: `contraindications` gate actions against medical limitations.

## Action metadata (target schema)
```json
{
  "slug": "walk_steps",
  "type": "core_habit",
  "category": "movement",
  "title": "Walk {target} steps today.",
  "why": "Walking improves circulation and cardiovascular health.",
  "verification": {"type": "sensor", "source": "healthkit/google_fit", "metric": "steps"},
  "difficulty": 1,
  "duration_min": 15,
  "contraindications": ["severe_joint_pain"],
  "level_scaling": {"1": 2000, "5": 5000, "10": 8000, "20": 10000},
  "weather_adaptations": {"rain": "indoor_march", "heat": "early_or_evening"},
  "alternatives": ["stretch", "chair_exercises"]
}
```

## Current implementation
- `plans/models.py::ActionDef` — full metadata: `slug, type, category, title, why,
  verification_type, verification_source, metric, level_scaling, difficulty, duration_min,
  contraindications, weather_adaptations, alternatives, is_active` (+ `target_for_level`).
- Fields added in `migrations/0009`; the 8 starter actions backfilled in `migrations/0010`.
- **Contraindications are enforced:** `daily.py::user_contraindications()` +
  `_resolve_safe()` gate unsafe actions and substitute a safe `alternative` (e.g. joint
  pain → walk/park replaced by stretch). Verified.
- Legacy `plans/data/knowledge_base.json` powers only the old full-plan/PDF, not the ritual.

## Boundaries (do NOT do here)
- Choosing which actions to show today → Behavior / AI Planner.
- Deciding if an action counts → Verification.

## Open / next
- Grow the library from 8 → hundreds of actions across all categories (all fields required).
- Have the AI Planner honor `weather_adaptations` (needs a weather input).
- Refine contraindication inference from the questionnaire (currently joint_pain + keyword scan).
