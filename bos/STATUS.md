# BOS — Implementation Status

_Traceability: each engine → where it lives → what's done vs open. Update this whenever
you build. Last updated: 2026-07-19._

Legend: ✅ done · 🟢 MVP-complete (minor/post-MVP open) · 🟡 partial · ⬜ not started

| Engine | Status | Code | Done | Open |
|--------|--------|------|------|------|
| 1 Behavior | 🟢 | `models.py` (Level, UserProgram, ActionDef), `daily.py`, `behavior.py`, `migrations/0008` | 20 levels + bands; core/mission split; level-scaled targets; ≥3/day; **per-level mission themes (categories unlock by level) + weakest-habit adaptation (mission order biased by category stability, persisted to `HabitStability`)** | finer per-level difficulty curves |
| 2 Knowledge | 🟡 | `models.py::ActionDef`, `daily.py`, `migrations/0008-0012` | **full metadata**; **contraindication gating + safe substitution live**; **100 actions across all 7 categories** (0011-0012); **refined inference** — 5 tags (joint/injury/**cardiac/balance/respiratory**); metadata contract enforced by tests | grow further (100 → hundreds); **wire weather (deferred to later version)** |
| 3 Verification | 🟢 | `verification.py`, `views.verify_action`, `models.py::ActionLog` | 5 verifier types + anti-cheat; web trust-based confirm; **server `/api/verify/` endpoint — resolves sensor/timer/location/photo/confirm, gentle anti-cheat, bridges to streak/tree + level check** | wearable/HealthKit/Fit/GPS adapters + the mobile client that posts to it (Track B) |
| 4 Level | 🟢 | `progression.py`, `views.py`, `Level` | mastery (40/30/20/10); band checks; promote/extend; **lazy nightly re-eval on ritual load; promote/extend messages surfaced (ritual banner + `step_done` JSON); level-up signal → progress celebration** | true scheduled cron (currently lazy on load); explicit tree blossom animation (→ Tree Engine) |
| 5 Recovery | 🟢 | `tree_state.py`, `daily.py`, `UserProgram.recovery_until` | inactivity days; 7-day window opens at ≥14 idle; **recovery multiplier applied in daily.py (effort metrics only — sleep/hydration never reduced); linear taper 0.4→1.0; gentle non-shaming welcome-back copy** | nightly auto-open (currently opens on next tree read); recovery→tree "welcome back" visual |
| 6 Tree | ✅ | `static/plans/tree-engine.js` (as-is), `tree_state.py`, `progress.html` | action-driven growth; level/health/dormant; zoom reveal; BG labels; **level-up animates the trunk/branches (mount prev level → `setLevel` to new, watched on the progress page)** | long-term events (birds/fruit/seasonal); recovery-renewal visual on return |
| 7 AI Planner | 🟢 | `ai_companion.py`, `reflection.py`, `daily.py`, `ritual.html` | 3 actions + why; AI warm line + **AI-written reflection question (same single call) + learning loop (recent reflection answers fed into the prompt)**; rule-based fallback throughout; reflection stored per day + admin | `/api/today` full payload (mobile, Track B); weather (deferred) |

## Cross-cutting / not yet built
- **Mobile app + sensor bridge** (HealthKit / Google Fit / Health Connect / GPS / camera).
- **API surface** for the mobile loop: `/api/today`, `/api/action/{id}/complete`, `/api/verify/*`, `/api/tree`.
- **Reflection AI-learning loop** (storage done, `0013`; feeding answers back to the companion is open).
- Extended `ActionDef` metadata migration (see Knowledge Engine).

## Path to 100% — remaining work, in order

**Track A — Web MVP (no mobile needed), do these first:**
1. ✅ **Level (4)** — lazy re-eval on load + promote/extend messages (ritual banner + step_done JSON)
   + level-up signal → progress celebration. _Remaining for full: a true scheduled cron._
2. ✅ **Tree (6)** — level-up now animates the trunk/branches (`setLevel` prev→new on the progress
   page). _Remaining: long-term events (birds/fruit/seasonal); recovery-renewal visual._
3. **Recovery (5) → 100%:** nightly auto-open of the recovery window (don't wait for a tree read);
   recovery → tree "welcome back" visual.
4. ✅ **AI Planner (7) — web parts:** AI-written reflection question (rule-pool fallback) + learning
   loop (recent reflections fed into the prompt), both in the existing single call. Habit-stability
   selection is handled by Behavior (1). _Remaining: `/api/today` (mobile, Track B)._
5. **Behavior (1) → 100%:** finer per-level difficulty curves (per-action/category, beyond linear scaling).
6. **Knowledge (2) → 100% (web parts):** grow library 100 → hundreds; broaden contraindication inference.

**Track B — needs the mobile app / infra (post-MVP):**
7. **Verification (3):** ✅ server `/api/verify/` endpoint built (all verifier types + anti-cheat).
   Remaining: wearable adapters (HealthKit / Google Fit / Health Connect / GPS / camera) + the mobile client that posts to it.
8. **AI Planner (7) → 100% (mobile parts):** `/api/today` full morning-payload endpoint.
9. **Knowledge (2):** wire `weather_adaptations` into selection (needs a weather input; deferred).
10. **Platform:** the API surface (`/api/*`) + the mobile app + sensor bridge.

_Ordering rule: Track A ships the emotional/retention loop on web; Track B unlocks sensor
verification once there's an app. Weather + mobile are deliberately deferred._

## Data models (built) — `plans/models.py`
`Level` · `ActionDef` · `UserProgram` · `ActionLog` · `HabitStability` · `TreeState` ·
`DailyAssignment` · `Reflection` (migrations `0007` schema, `0008` seed, `0011-0012` library, `0013` reflection).

## Verification of current build
`python manage.py test plans` → 44/44 green. Local dev DB = sqlite. The ritual runs the
new ActionDef flow end-to-end (task+why → verified ActionLog → tree growth).
