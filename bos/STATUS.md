# BOS — Implementation Status

_Traceability: each engine → where it lives → what's done vs open. Update this whenever
you build. Last updated: 2026-07-18._

Legend: ✅ done · 🟡 partial · ⬜ not started

| Engine | Status | Code | Done | Open |
|--------|--------|------|------|------|
| 1 Behavior | 🟡 | `models.py` (Level, UserProgram, ActionDef), `daily.py`, `migrations/0008` | 20 levels + bands seeded; core/mission split; level-scaled targets; ≥3 actions/day | per-level mission themes; behavioral adaptation to weakest habits |
| 2 Knowledge | 🟡 | `models.py::ActionDef`, `daily.py`, `migrations/0008-0010` | **full metadata** (incl. difficulty/duration/contraindications/weather/alternatives); **contraindication gating + safe-alternative substitution live**; 8 starter actions | grow library to hundreds; wire weather into planner |
| 3 Verification | 🟡 | `verification.py`, `models.py::ActionLog` | 5 verifier types + anti-cheat; web = trust-based confirm | `/api/verify/sensor` + `/api/verify/photo`; wearable/HealthKit/Fit/GPS adapters |
| 4 Level | 🟡 | `progression.py`, `Level` | mastery score (40/30/20/10); band checks; promote/extend on completion | nightly re-eval; UI messages; level-up → tree event |
| 5 Recovery | 🟡 | `tree_state.py`, `UserProgram.recovery_until` | inactivity days; 7-day recovery window opens at ≥14 idle | apply recovery target multiplier in `daily.py`; welcome-back taper |
| 6 Tree | ✅ | `static/plans/tree-engine.js` (as-is), `tree_state.py`, `progress.html` | action-driven growth; level/health/dormant; visibility-gated zoom reveal; BG labels | route level-up/long-term events (branches/flowers/birds) explicitly |
| 7 AI Planner | 🟡 | `ai_companion.py`, `daily.py`, `ritual.html` | rule-based 3 actions + why; AI warm line w/ fallback | `/api/today` full morning payload; weather/contraindications/stability; reflection question |

## Cross-cutting / not yet built
- **Mobile app + sensor bridge** (HealthKit / Google Fit / Health Connect / GPS / camera).
- **API surface** for the mobile loop: `/api/today`, `/api/action/{id}/complete`, `/api/verify/*`, `/api/tree`.
- **Reflection storage** + AI learning loop.
- Extended `ActionDef` metadata migration (see Knowledge Engine).

## Data models (built) — `plans/models.py`
`Level` · `ActionDef` · `UserProgram` · `ActionLog` · `HabitStability` · `TreeState` ·
`DailyAssignment` (migrations `0007` schema, `0008` seed).

## Verification of current build
`python manage.py test plans` → 18/18 green. Local dev DB = sqlite. The ritual runs the
new ActionDef flow end-to-end (task+why → verified ActionLog → tree growth).
