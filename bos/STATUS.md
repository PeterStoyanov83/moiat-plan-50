# BOS — Implementation Status

_Traceability: each engine → where it lives → what's done vs open. Update this whenever
you build. Last updated: 2026-07-18._

Legend: ✅ done · 🟢 MVP-complete (minor/post-MVP open) · 🟡 partial · ⬜ not started

| Engine | Status | Code | Done | Open |
|--------|--------|------|------|------|
| 1 Behavior | 🟡 | `models.py` (Level, UserProgram, ActionDef), `daily.py`, `migrations/0008` | 20 levels + bands seeded; core/mission split; level-scaled targets; ≥3 actions/day | per-level mission themes; behavioral adaptation to weakest habits |
| 2 Knowledge | 🟡 | `models.py::ActionDef`, `daily.py`, `migrations/0008-0012` | **full metadata**; **contraindication gating + safe substitution live**; **100 actions across all 7 categories** (0011-0012); **refined inference** — 5 tags (joint/injury/**cardiac/balance/respiratory**); metadata contract enforced by tests | grow further (100 → hundreds); **wire weather (deferred to later version)** |
| 3 Verification | 🟡 | `verification.py`, `models.py::ActionLog` | 5 verifier types + anti-cheat; web = trust-based confirm | `/api/verify/sensor` + `/api/verify/photo`; wearable/HealthKit/Fit/GPS adapters |
| 4 Level | 🟡 | `progression.py`, `Level` | mastery score (40/30/20/10); band checks; promote/extend on completion | nightly re-eval; UI messages; level-up → tree event |
| 5 Recovery | 🟢 | `tree_state.py`, `daily.py`, `UserProgram.recovery_until` | inactivity days; 7-day window opens at ≥14 idle; **recovery multiplier applied in daily.py (effort metrics only — sleep/hydration never reduced); linear taper 0.4→1.0; gentle non-shaming welcome-back copy** | nightly auto-open (currently opens on next tree read); recovery→tree "welcome back" visual |
| 6 Tree | ✅ | `static/plans/tree-engine.js` (as-is), `tree_state.py`, `progress.html` | action-driven growth; level/health/dormant; visibility-gated zoom reveal; BG labels | route level-up/long-term events (branches/flowers/birds) explicitly |
| 7 AI Planner | 🟡 | `ai_companion.py`, `daily.py`, `reflection.py`, `ritual.html` | rule-based 3 actions + why; AI warm line w/ fallback; **reflection question (rule-based pool) + storage (`Reflection` model) + end-of-ritual UI + admin** | `/api/today` full morning payload; weather/stability; AI-written reflection |

## Cross-cutting / not yet built
- **Mobile app + sensor bridge** (HealthKit / Google Fit / Health Connect / GPS / camera).
- **API surface** for the mobile loop: `/api/today`, `/api/action/{id}/complete`, `/api/verify/*`, `/api/tree`.
- **Reflection storage** + AI learning loop.
- Extended `ActionDef` metadata migration (see Knowledge Engine).

## Data models (built) — `plans/models.py`
`Level` · `ActionDef` · `UserProgram` · `ActionLog` · `HabitStability` · `TreeState` ·
`DailyAssignment` · `Reflection` (migrations `0007` schema, `0008` seed, `0011-0012` library, `0013` reflection).

## Verification of current build
`python manage.py test plans` → 31/31 green. Local dev DB = sqlite. The ritual runs the
new ActionDef flow end-to-end (task+why → verified ActionLog → tree growth).
