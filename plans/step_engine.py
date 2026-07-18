"""Daily single-step engine for the "Една стъпка" ritual.

The knowledge base already holds every step we need (movement/nutrition by
level, plus social and finance pools). This module serves those tasks **one at
a time**: it builds the pool of steps eligible for a given person, offers the
next one they haven't done today, and records completions.

Personalization reuses the existing rule-based helpers — nothing new invented:
- levels come from ``movement_level_for`` / ``nutrition_level_for``
- the profile (``determine_profile``) nudges which category is offered first

The rule-based ``offer_step`` is the seam where an AI companion later plugs in
("днес направи само това").
"""
import random
from datetime import date

from django.utils import timezone

from .knowledge_base import load_kb, movement_level_for, nutrition_level_for
from .profile_logic import (
    determine_profile,
    PROFILE_LEK_START,
    PROFILE_OTSLABVANE,
    PROFILE_ENERGIYA,
    PROFILE_SOCIALEN,
    PROFILE_BALANS,
)

# Categories a step can belong to (matches KB top-level keys).
MOVEMENT, NUTRITION, SOCIAL, FINANCE = 'movement', 'nutrition', 'social', 'finance'

# Which category each profile leans toward — surfaced first, gently.
PROFILE_PRIORITY = {
    PROFILE_LEK_START:  [MOVEMENT, NUTRITION, SOCIAL, FINANCE],
    PROFILE_OTSLABVANE: [NUTRITION, MOVEMENT, SOCIAL, FINANCE],
    PROFILE_ENERGIYA:   [MOVEMENT, NUTRITION, SOCIAL, FINANCE],
    PROFILE_SOCIALEN:   [SOCIAL, MOVEMENT, NUTRITION, FINANCE],
    PROFILE_BALANS:     [MOVEMENT, NUTRITION, SOCIAL, FINANCE],
}


def _icon_for(category, text):
    """Pick a front-end icon hint for a step (matches the ritual template's SVGs)."""
    t = text.lower()
    if 'вода' in t:
        return 'water'
    if category == MOVEMENT:
        if any(w in t for w in ('разтяг', 'гимнастика', 'йога', 'баланс', 'планк', 'клек')):
            return 'stretch'
        return 'walk'
    if category == NUTRITION:
        return 'salad'
    if category == SOCIAL:
        return 'friend'
    if category == FINANCE:
        return 'coin'
    return 'walk'


def eligible_steps(response):
    """All steps that fit this person, as ordered dicts {category, text, icon}.

    Ordered by the profile's category priority so the "first" offered step
    matches what the user most needs — but every category stays available.
    """
    kb = load_kb()
    m_level = movement_level_for(response)
    n_level = nutrition_level_for(response)

    by_category = {
        MOVEMENT:  list(kb['movement']['levels'][str(m_level)]['tasks']),
        NUTRITION: list(kb['nutrition']['levels'][str(n_level)]['tasks']),
        SOCIAL:    list(kb['social']['tasks']),
        FINANCE:   list(kb['finance']['tasks']),
    }

    profile = determine_profile(response)
    order = PROFILE_PRIORITY.get(profile, PROFILE_PRIORITY[PROFILE_BALANS])

    steps = []
    for category in order:
        for text in by_category[category]:
            steps.append({'category': category, 'text': text, 'icon': _icon_for(category, text)})
    return steps


def _completed_today_texts(response, today):
    return set(
        response.step_completions.filter(completed_on=today).values_list('step_text', flat=True)
    )


def offer_step(response, exclude=None, today=None):
    """Return the next single step to offer, or ``None`` if none remain today.

    Skips steps already completed today and any in ``exclude`` (used by "swap":
    show me a different one). Rotation is stable within a day but advances as
    steps get done, so the user sees fresh steps without repeats.
    """
    today = today or timezone.localdate()
    exclude = set(exclude or [])
    done = _completed_today_texts(response, today)

    pool = [s for s in eligible_steps(response) if s['text'] not in done and s['text'] not in exclude]
    if not pool:
        return None

    # Rotate deterministically by (person, day, progress) so it feels fresh
    # but is reproducible within a request.
    seed = (response.pk or 0) + today.toordinal() + len(done)
    return pool[seed % len(pool)]


def offer_choices(response, n=3, exclude=None, today=None):
    """Return up to ``n`` distinct step options (A/B/C) to pick from today.

    Skips steps done today and any in ``exclude``; prefers variety across
    categories. Stable within a day, advances as steps get done.
    """
    today = today or timezone.localdate()
    exclude = set(exclude or [])
    done = _completed_today_texts(response, today)
    pool = [s for s in eligible_steps(response) if s['text'] not in done and s['text'] not in exclude]
    if not pool:
        return []
    rng = random.Random((response.pk or 0) + today.toordinal() + len(done))
    # spread across categories: one per category first, then fill.
    by_cat = {}
    for s in pool:
        by_cat.setdefault(s['category'], []).append(s)
    for lst in by_cat.values():
        rng.shuffle(lst)
    chosen, cats = [], list(by_cat.keys())
    rng.shuffle(cats)
    for c in cats:
        if len(chosen) < n and by_cat[c]:
            chosen.append(by_cat[c].pop(0))
    leftovers = [s for lst in by_cat.values() for s in lst]
    rng.shuffle(leftovers)
    chosen += leftovers[: max(0, n - len(chosen))]
    return chosen[:n]


def mark_done(response, step_text, category, today=None):
    """Record a completed step (idempotent per text per day)."""
    today = today or timezone.localdate()
    obj, created = response.step_completions.get_or_create(
        step_text=step_text, completed_on=today,
        defaults={'category': category},
    )
    return created


def today_progress(response, today=None):
    """Steps done today + a simple consecutive-day streak."""
    today = today or timezone.localdate()
    done_today = response.step_completions.filter(completed_on=today).count()

    days = sorted(
        set(response.step_completions.values_list('completed_on', flat=True)), reverse=True
    )
    streak, expected = 0, today
    for d in days:
        if d == expected:
            streak += 1
            expected = expected.fromordinal(expected.toordinal() - 1)
        elif d < expected:
            break
    return {'done_today': done_today, 'streak': streak}


BG_WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд']


def weekly_history(response, days=7, today=None):
    """Per-day completion counts for the last ``days`` days (oldest first)."""
    today = today or timezone.localdate()
    qs = response.step_completions
    out = []
    for i in range(days - 1, -1, -1):
        d = date.fromordinal(today.toordinal() - i)
        out.append({
            'date': d,
            'label': BG_WEEKDAYS[d.weekday()],
            'count': qs.filter(completed_on=d).count(),
            'is_today': d == today,
        })
    return out
