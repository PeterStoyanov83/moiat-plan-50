"""Level Master Checker + progression (see design/HABIT_ENGINE_SPEC.md §6).

Levels are SYSTEM-driven, never chosen by the user. Everyone starts at level 1.
After a level's minimum period, mastery is evaluated: pass → next level; not
ready → extend the SAME level by 7 days (never fail, never reset, keep core habits).
"""
import datetime
from django.db.models import Count
from .models import Level, ActionLog

# Mastery weights (§5): consistency .40, verified actions .30, core stability .20, missions .10
W_CONSISTENCY, W_VERIFIED, W_CORE, W_MISSION = 0.40, 0.30, 0.20, 0.10
EXTEND_DAYS = 7


def _pct(n, d):
    return 0.0 if not d else round(100.0 * n / d, 1)


def scores_for_period(response, start, end):
    """Compute the four sub-scores over [start, end] (inclusive dates)."""
    total_days = max(1, (end - start).days + 1)
    logs = list(ActionLog.objects.filter(response=response, date__gte=start, date__lte=end))
    done = [l for l in logs if l.status in ActionLog.COUNTS_AS_DONE]

    active_days = len({l.date for l in done})
    consistency = _pct(active_days, total_days)

    completion = _pct(len(done), len(logs)) if logs else 0.0

    verified = [l for l in done if l.status == ActionLog.VERIFIED]
    verified_score = _pct(len(verified), len(done)) if done else 0.0

    # core-habit stability = share of active days that included a core habit
    core_days = len({l.date for l in done if l.action and l.action.type == 'core_habit'})
    core_stability = _pct(core_days, total_days)

    mission_days = len({l.date for l in done if l.action and l.action.type == 'growth_mission'})
    mission_score = _pct(mission_days, total_days)

    return {
        'total_days': total_days, 'active_days': active_days,
        'consistency': consistency, 'completion': completion,
        'verified': verified_score, 'core_stability': core_stability,
        'missions': mission_score,
    }


def mastery_score(s):
    return round(
        W_CONSISTENCY * s['consistency'] + W_VERIFIED * s['verified']
        + W_CORE * s['core_stability'] + W_MISSION * s['missions'], 1)


def evaluate_level(program, today=None):
    """Decide promote / extend / in_progress for a UserProgram.

    Returns dict {decision, scores, mastery, level}. Mutates + saves the program
    on promote/extend. Never lowers the level, never resets history.
    """
    today = today or datetime.date.today()
    start = program.level_started_on
    required_days = 14 + program.extended_days
    end = today

    scores = scores_for_period(program.response, start, end)
    mastery = mastery_score(scores)

    # Still inside the minimum window → keep going.
    if (today - start).days + 1 < required_days:
        return {'decision': 'in_progress', 'scores': scores, 'mastery': mastery,
                'level': program.current_level}

    try:
        band = Level.objects.get(number=program.current_level)
    except Level.DoesNotExist:
        band = None

    passed = band and (
        scores['consistency'] >= band.consistency_req
        and scores['completion'] >= band.completion_req
        and scores['core_stability'] >= band.core_habit_req
    )

    if passed and program.current_level < 20:
        program.current_level += 1
        program.level_started_on = today
        program.extended_days = 0
        program.save(update_fields=['current_level', 'level_started_on', 'extended_days'])
        return {'decision': 'promote', 'scores': scores, 'mastery': mastery,
                'level': program.current_level,
                'message': 'Дървото ти пуска нов клон. 🌱'}

    if passed:  # already at 20 — sustained mastery, stay
        return {'decision': 'in_progress', 'scores': scores, 'mastery': mastery,
                'level': 20}

    # Not ready → extend the same level, keep core habits, change missions/difficulty.
    program.extended_days += EXTEND_DAYS
    program.save(update_fields=['extended_days'])
    return {'decision': 'extend', 'scores': scores, 'mastery': mastery,
            'level': program.current_level,
            'message': 'Твоите корени укрепват. Нека им дадем още малко време.'}
