"""Action Verification Engine (see design/HABIT_ENGINE_SPEC.md §3).

Pure logic — no device SDKs here. The mobile/web layer supplies the measured
value (sensor aggregate, timer duration, GPS minutes, photo AI confidence);
this module decides the outcome. Trust-based, never shaming.
"""
from .models import ActionLog

# Anti-cheat: a claim this many times over the measured value is implausible.
_CHEAT_RATIO = 3.0


def _target(action, level):
    t = action.target_for_level(level) if action else None
    return float(t) if t is not None else None


def verify(action, *, level=1, measured=None, claimed=None, minutes=None,
           confidence=None, confirmed=False):
    """Return (status, measured_value, confidence) for one attempt.

    status ∈ ActionLog.{VERIFIED, CONFIRMED, UNVERIFIED, REJECTED, PENDING}
    """
    vt = action.verification_type if action else 'confirm'

    if vt == 'sensor':
        target = _target(action, level)
        if measured is None:
            return ActionLog.PENDING, None, None
        # Anti-cheat: claim far above what the device recorded → not counted.
        if claimed is not None and measured > 0 and claimed > measured * _CHEAT_RATIO:
            return ActionLog.UNVERIFIED, measured, None
        if target is None or measured >= target:
            return ActionLog.VERIFIED, measured, 1.0
        return ActionLog.UNVERIFIED, measured, None

    if vt == 'timer':
        target = _target(action, level)  # minutes
        if minutes is None:
            return ActionLog.PENDING, None, None
        if target is None or minutes >= target:
            return ActionLog.VERIFIED, minutes, 1.0
        return ActionLog.UNVERIFIED, minutes, None

    if vt == 'location':
        target = _target(action, level) or 20  # minutes outside
        if minutes is None:
            return ActionLog.PENDING, None, None
        return (ActionLog.VERIFIED, minutes, 1.0) if minutes >= target \
            else (ActionLog.UNVERIFIED, minutes, None)

    if vt == 'photo_ai':
        if confidence is None:
            return ActionLog.PENDING, None, None
        return (ActionLog.VERIFIED, None, confidence) if confidence >= 0.6 \
            else (ActionLog.UNVERIFIED, None, confidence)

    # confirm — trust-based, always accepted, never punished
    return (ActionLog.CONFIRMED, None, None) if confirmed \
        else (ActionLog.PENDING, None, None)


def log_attempt(response, action, date, *, level=1, **kwargs):
    """Verify + persist an ActionLog row. Returns the row."""
    status, measured, confidence = verify(action, level=level, **kwargs)
    return ActionLog.objects.create(
        response=response, action=action, date=date, status=status,
        verification_type=(action.verification_type if action else ''),
        claimed_value=kwargs.get('claimed'), measured_value=measured,
        confidence=confidence, source=(action.verification_source if action else ''),
    )


# Gentle message when an attempt doesn't count (anti-cheat / under target).
GENTLE_UNVERIFIED = 'Изглежда, че този навик има нужда от малко повече внимание днес.'
