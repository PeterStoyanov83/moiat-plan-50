# 3 — Verification Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **decide whether an action actually happened.** It does not pick actions, score
> levels, or move the tree — it only returns an outcome for one attempt.

## Responsibility
Turn an attempt into a trustworthy outcome. **Verify whenever technically possible.**

## Rules (binding)
- **Verification hierarchy (prefer higher):**
  Sensor → Wearables → HealthKit → Google Fit → Health Connect → GPS → AI photo →
  Timer → **Manual confirmation (last resort)**.
- **Never blindly trust user input** when objective verification is possible.
- **Anti-cheat, never shame:** if a claim is implausible vs measured data (e.g. claims
  10 000 steps, device shows 200), do **not** count it — and respond gently:
  *"Изглежда, че този навик има нужда от малко повече внимание днес."*
- Manual confirmation (e.g. "call your mother") is always accepted, never punished.

## Outcome model
`ActionLog.status ∈ {pending, verified, unverified, confirmed, rejected}`.
`COUNTS_AS_DONE = {verified, confirmed}`. `verified` = objective; `confirmed` = trusted manual.

## Current implementation
- `plans/verification.py::verify()` — sensor / timer / location / photo_ai / confirm +
  anti-cheat ratio; `log_attempt()` persists an `ActionLog`.
- `plans/models.py::ActionLog` — `status, verification_type, claimed_value,
  measured_value, confidence, source`.
- **Web shell:** taps are trust-based `confirmed` (no browser sensors). **Mobile:** must
  post objective data to the verify endpoints so `sensor/timer/location/photo` resolve to
  `verified`.

## Boundaries (do NOT do here)
- Difficulty/target for a level → Behavior Engine (`ActionDef.target_for_level`).
- Whether the user levels up → Level Engine.

## Open / next
- `/api/verify/sensor` (daily device aggregates) + `/api/verify/photo` (AI confidence).
- Wearable/HealthKit/Google Fit/Health Connect adapters (mobile).
- GPS/location session verification with **privacy-first** handling (no location history).
