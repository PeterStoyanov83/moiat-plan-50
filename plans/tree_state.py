"""Living Tree state derivation + inactivity/recovery (spec §7–§9).

The tree grows ONLY from completed+verified actions, never from elapsed time.
Level (system-driven) thickens the trunk; inactivity gently fades health; the
wood and roots never regress. This module is the single source the progress
page reads to feed the front-end engine (completedActions/level/health/dormant).
"""
import datetime
from .models import ActionLog, UserProgram, TreeState, StepCompletion

# Growth stage by program level (spec §7 "Tree States")
def growth_stage_for(level, total_done):
    if total_done <= 0:
        return 0                     # seed
    if level >= 20:
        return 6                     # strong, unique
    if level >= 15:
        return 5                     # mature
    if level >= 10:
        return 4                     # growing branches
    if level >= 5:
        return 3                     # young tree
    if total_done >= 3:
        return 2                     # small stem — first stable habits
    return 1                         # roots — first completed actions


# Inactivity → health (spec §8). Gentle: leaves never below ~40%, wood/roots stay.
def health_for_inactivity(days):
    if days is None or days < 3:
        return 100, False
    if days < 7:
        return 75, False             # leaves less vibrant
    if days < 14:
        return 50, False             # some leaves fall, growth pauses
    return 40, True                  # dormant — roots remain


def last_activity_date(response):
    log = (ActionLog.objects
           .filter(response=response, status__in=ActionLog.COUNTS_AS_DONE)
           .order_by('-date').values_list('date', flat=True).first())
    if log:
        return log
    # legacy fallback: StepCompletion
    return (StepCompletion.objects.filter(response=response)
            .order_by('-completed_on').values_list('completed_on', flat=True).first())


def total_done(response):
    n = ActionLog.objects.filter(
        response=response, status__in=ActionLog.COUNTS_AS_DONE).count()
    if n:
        return n
    return StepCompletion.objects.filter(response=response).count()  # legacy


def in_recovery(program, today):
    return bool(program and program.recovery_until and today <= program.recovery_until)


RECOVERY_WINDOW_DAYS = 7
RECOVERY_MIN_FACTOR = 0.4        # start at ~40% of target on return...


def recovery_factor(program, today):
    """Target multiplier during the recovery window (spec §5: reduce workload,
    then restore momentum). Starts at RECOVERY_MIN_FACTOR on the day of return and
    tapers linearly back to 1.0 over RECOVERY_WINDOW_DAYS. 1.0 when not recovering."""
    if not in_recovery(program, today):
        return 1.0
    days_left = max(0, min(RECOVERY_WINDOW_DAYS, (program.recovery_until - today).days))
    progress = (RECOVERY_WINDOW_DAYS - days_left) / RECOVERY_WINDOW_DAYS   # 0 → 1
    return RECOVERY_MIN_FACTOR + (1 - RECOVERY_MIN_FACTOR) * progress


def compute_tree_state(response, today=None, persist=True):
    """Derive + (optionally) cache the tree state for a response."""
    today = today or datetime.date.today()
    program, _ = UserProgram.objects.get_or_create(response=response)

    done = total_done(response)
    level = program.current_level
    last = last_activity_date(response)
    days_idle = (today - last).days if last else None
    health, dormant = health_for_inactivity(days_idle)

    # Returning after a long gap → open a 7-day recovery window (reduced targets).
    if days_idle is not None and days_idle >= 14 and not program.recovery_until:
        program.recovery_until = today + datetime.timedelta(days=7)
        program.save(update_fields=['recovery_until'])

    stage = growth_stage_for(level, done)
    state = {
        'age': done, 'growth_stage': stage, 'level': level,
        'health': health, 'dormant': dormant,
        'last_activity': last.isoformat() if last else None,
        'recovery': in_recovery(program, today),
    }
    if persist:
        TreeState.objects.update_or_create(
            response=response,
            defaults=dict(age=done, growth_stage=stage, level=level,
                          health=health, dormant=dormant, last_activity=last),
        )
    return state
