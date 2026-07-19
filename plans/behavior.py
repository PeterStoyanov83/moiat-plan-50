"""Behavior Engine (bos/engines/01-behavior-engine.md).

Owns the *shape* of the journey that isn't already in the Level/Knowledge data:
 - per-level **mission themes** (which categories the journey emphasises as levels rise), and
 - **behavioral adaptation** — bias mission selection toward the user's weakest habits.

It only orders the *missions* pool; core habits stay first (they are permanent
foundations). It reads ActionLog (Verification's output) but never verifies, promotes,
or renders — those belong to other engines.
"""
from collections import Counter
from datetime import timedelta
from .models import ActionLog, HabitStability

STABILITY_WINDOW_DAYS = 14


def emphasized_categories(level):
    """The level's mission theme: categories the journey emphasises so far.
    Foundations first; richer domains unlock as the user progresses."""
    cats = ['movement', 'hydration', 'mind']       # L1+ foundations
    if level >= 4:
        cats += ['nutrition', 'sleep']
    if level >= 8:
        cats += ['social']
    if level >= 12:
        cats += ['financial']
    return cats


def category_stability(response, today, window=STABILITY_WINDOW_DAYS):
    """0..100 per category — how *established* each habit is, from recent completed
    actions. Higher = stronger. No history → empty (everything equally weak)."""
    since = today - timedelta(days=window)
    rows = ActionLog.objects.filter(
        response=response, date__gte=since, status__in=ActionLog.COUNTS_AS_DONE,
    ).values_list('action__category', flat=True)
    counts = Counter(c for c in rows if c)
    return {cat: min(100, n * 25) for cat, n in counts.items()}


def _persist_stability(response, stab):
    """Snapshot the rolling stability so the Level engine / admin can read it."""
    for key, val in stab.items():
        HabitStability.objects.update_or_create(
            response=response, key=key, defaults={'stability': val})


def order_missions(response, missions, level, today, rng):
    """Order the missions pool: theme-emphasised categories first, then the user's
    weakest categories, with a stable per-day random tiebreak. Reinforces shaky
    habits without ever removing variety."""
    stab = category_stability(response, today)
    _persist_stability(response, stab)
    emphasized = set(emphasized_categories(level))
    tiebreak = {a.slug: rng.random() for a in missions}

    def key(a):
        return (
            0 if a.category in emphasized else 1,   # in-theme categories first
            stab.get(a.category, 0),                # weakest (lowest stability) first
            tiebreak[a.slug],                       # stable daily shuffle
        )

    return sorted(missions, key=key)
