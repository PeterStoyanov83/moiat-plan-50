# Habit Evolution Engine — Design Spec (v1)

_Behavioral transformation system for „1Step" („Една стъпка"). NOT a checkbox tracker: the
tree grows from **verified real behavior**, not clicks. Written 2026-07-17. Status: DESIGN — not built._

> **Front-end is ~ready.** `plans/static/plans/tree-engine.js` already exposes everything the
> Living Tree section below needs: `completedActions` + `queueActions()/playReveal()` (action-driven
> growth with zoom-into-leaf), `setLevel(1..20)` (trunk girth = discipline), `setHealth(0..100)` +
> `setDormant()` (gentle inactivity fade — leaves never < ~40%, wood/roots never regress),
> `GROWTH_STAGES` (9 BG-labelled stages), seasons. **The work is BACKEND + wiring these from real data.**

## 1. Backend architecture (Django, app `plans`)
Layered services (keep views thin):
- `verification/` — pluggable verifiers per `verification_type` (sensor, timer, location, photo_ai, confirm).
- `progression.py` — Level Master Checker (mastery score, level requirements, extend-on-not-ready).
- `tree_state.py` — derives tree params (stage, level, health, dormant) from user activity; single source the template reads.
- `inactivity.py` — days-since-last-verified-action → health/dormant + recovery mode.
- `ai_companion.py` (exists) — extend: adaptive difficulty + mission selection.
- Existing: `step_engine`, `knowledge_base.json`, `profile_logic`, `ai_companion`.

## 2. Database models (new)
```python
class Level(Model):                 # static 1..20 config (seed via fixture/JSON)
    number, min_days=14, consistency_req, completion_req, core_habit_req  # thresholds per band

class ActionDef(Model):             # the action library (replaces/extends knowledge_base.json)
    slug, type(core_habit|growth_mission), category(movement|nutrition|sleep|hydration|social|mind)
    title, why, verification_type, verification_source, metric, level_scaling(JSON)  # {level:target}

class UserProgram(Model):           # one per user
    user FK, current_level=1, level_started_on, extended_days=0, recovery_until(null)

class DailyAssignment(Model):       # the 3+ actions offered for a given day
    user FK, date, action FK, slot(core|mission)

class ActionLog(Model):             # one attempt/completion
    user FK, action FK, date, status(pending|verified|unverified|confirmed|rejected)
    verification_type, claimed_value, measured_value, confidence, source, created_at

class HabitStability(Model):        # rolling per (user, category/action)
    user FK, key, stability(0..100), updated_at

class TreeState(Model):             # cache of derived tree (see §10 model), recomputed on activity
    user FK, age, growth_stage, health, branches, leaves, flowers, dormant, level, last_activity
```
StepCompletion (existing) → migrate into `ActionLog` (status=confirmed) or keep as legacy source.

## 3. Verification engine
`verify(action_log) -> {status, measured_value, confidence}` dispatched by `verification_type`:
1. **sensor** — compare device steps/sleep vs `metric/target` (HealthKit / Google Fit / Health Connect). success if measured ≥ target.
2. **timer** — session kept active ≥ required minutes (client posts start+end + heartbeat).
3. **location** — ≥ N min outside via GPS + movement; **privacy: never persist location history**, only a boolean+duration.
4. **photo_ai** — Claude vision estimates {vegetables, protein, portion} → confidence score; store score, not the photo long-term.
5. **confirm** — trust-based (e.g. „call your mother"); always accepted, never punished.

**Anti-cheating:** if claimed ≫ measured (e.g. claims 10 000 steps, sensor 200) → status=`unverified`, do NOT count, message (never shame): „Изглежда, че този навик има нужда от малко повече внимание днес."

## 4. Sensor integration strategy
Mobile shell (or PWA + Health Connect / HealthKit bridge) posts signed daily aggregates to
`POST /api/verify/sensor`. Server never trusts client claims for sensor actions — it reconciles
against the posted device metric. Permissions requested lazily, per-action, with clear purpose.

## 5. AI adaptation logic
Per user, after each level eval + on recovery: `ai_companion` chooses today's mission mix and
scales core-habit targets within the level band (via `level_scaling`), biased by weakest
`HabitStability` and the user's rhythm. Tone: warm, no pressure, „сравнявай се само със себе си от вчера".

## 6. Level progression algorithm
Never auto-advance at 14 days. After ≥ `min_days`, compute **Mastery Score**:
`0.40*consistency + 0.30*verified_completion + 0.20*core_habit_stability + 0.10*missions`.
- consistency = active_days / total_days; requirements per band:
  L1–5: 80/70/75 · L6–10: 80/75/80 · L11–15: 85/80/85 · L16–20: 90/85/90 (consistency/completion/core%).
- **Pass** → level+1, major tree growth event (`setLevel`, new branch/flowers, blossom reveal).
- **Not ready** → **extend +7 days**, change missions/difficulty/reminders, **keep core habits**;
  message: „Твоите корени укрепват. Нека им дадем още малко време." Never „провали се", never reset.

## 7. Tree growth algorithm (map to existing engine)
- Growth stage ← level: Seed(0) · Roots(first actions) · Stem(first stable habits) · Young(L5) · Branches(L10) · Mature(L15) · Strong/unique(L20).
- **Daily** verified action → `queueActions(total)` → zoom-into-leaf reveal (already built).
- **Level completion** → `setLevel(n)` (trunk thickens + glimmer ripple) + blossom.
- **Long-term** → seasonal changes / fruits / birds (birds+fruit = future engine additions).
- Tree grows ONLY from completed+verified actions, never from elapsed time.

## 8. Inactivity handling (drive `setHealth`/`setDormant` from `days_since_last_verified`)
- **3 days** → `setHealth(~75)` (leaves less vibrant). „Дървото ти чака следващата капка грижа."
- **7 days** → `setHealth(~50)` (some leaves fall, growth pauses). „Всяка градина има нужда от внимание. Една малка стъпка е достатъчна."
- **14 days** → `setDormant(true)` (roots strong, no regression). „Корените ти са още там. Да започнем с една малка стъпка."

## 9. Recovery mode
On return after inactivity: **do not restart**. Set `UserProgram.recovery_until = today+7`.
First 7 days scale targets down (e.g. 8000→3000 steps) via `level_scaling` override. Goal: restore momentum.

## 10. JSON schemas
Action (library):
```json
{"id":"walk_2000","type":"core_habit","category":"movement","title":"Walk 2000 steps today.",
 "why":"Walking improves circulation and cardiovascular health.",
 "verification":{"type":"phone_sensor","required":true,"source":"healthkit/google_fit","metric":"steps","target":2000},
 "levelScaling":{"level_1":2000,"level_5":5000,"level_10":8000,"level_20":10000}}
```
Tree state (API):
```json
{"user_id":123,"tree":{"age":120,"growth_stage":4,"health":82,"branches":34,"leaves":420,
 "flowers":3,"dormant":false,"last_activity":"2026-07-17"},
 "habits":{"walking":{"stability":87},"hydration":{"stability":72}}}
```

## 11. API endpoints
- `GET  /api/today` → 3+ `DailyAssignment` (core + missions) with per-action verification spec.
- `POST /api/action/{id}/complete` → body: claimed value / timer / confirm → runs verifier → status.
- `POST /api/verify/sensor` → daily device aggregates (steps, sleep…) for reconciliation.
- `POST /api/verify/photo` → meal photo → AI confidence.
- `GET  /api/tree` → TreeState JSON (§10) — the template feeds this into `mountTree`.
- `GET  /api/progress` → level, mastery breakdown, streak, stability.
- (internal) nightly job: recompute stability, inactivity health, level eval.

## 12. Mobile integration requirements
- Health permissions: HealthKit (iOS), Google Fit / **Health Connect** (Android).
- Background/period sync of aggregates; foreground timer + GPS sessions; camera for meal photos.
- Privacy-first: minimal scopes, no raw location/photo retention, on-device where possible.

---
### Immediate next steps (when execution resumes)
1. `ActionDef` + `ActionLog` + `UserProgram` models & migration; seed level config + a few core actions.
2. `verification/` skeleton with `confirm` + `timer` verifiers (no device dep) to prove the loop.
3. `tree_state.py` → wire `setLevel/setHealth/setDormant` + `queueActions` into `progress.html` from `/api/tree`.
4. Level Master Checker (§6) + extend-on-not-ready.
5. Inactivity/recovery (§8–9). Then sensor + photo verifiers (device-dependent).
