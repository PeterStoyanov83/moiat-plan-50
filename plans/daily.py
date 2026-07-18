"""Daily Action System (spec: bos/engines/01-behavior-engine.md + 07-ai-planner-engine.md).

Serves each day's actions from the ActionDef library — core habits (permanent)
first, then a growth mission for variety — scaled to the user's system-driven
level. Every card carries its title AND its `why`. Contraindicated actions are
gated for safety (Constitution: actions must respect medical limitations).
"""
import random
from django.utils import timezone
from .models import ActionDef, ActionLog, UserProgram

ICON_BY_CATEGORY = {
    'movement': 'walk', 'nutrition': 'salad', 'hydration': 'water',
    'sleep': 'sleep', 'social': 'friend', 'mind': 'stretch', 'financial': 'coin',
}


def _title_for(action, target):
    """Make the level-scaled target visible in the task text."""
    t = action.title
    if target is None:
        return t
    tv = int(target)
    if action.metric == 'steps':
        return f'Извърви {tv} крачки днес.'
    if action.metric == 'glasses':
        return f'Изпий {tv} чаши вода днес.'
    if action.metric == 'hours':
        return f'Спи поне {tv} часа тази нощ.'
    if action.metric == 'minutes':
        return f'{t.rstrip(".")} — {tv} мин.'
    return t


def card(action, level):
    target = action.target_for_level(level)
    return {
        'id': action.slug,
        'text': _title_for(action, target),   # task
        'why': action.why,                     # the "why"
        'category': action.category,
        'type': action.type,
        'verification': action.verification_type,
        'target': target,
        'icon': ICON_BY_CATEGORY.get(action.category, 'walk'),
    }


# -- Safety: contraindication gating -----------------------------------------

def user_contraindications(response):
    """Derive contraindication tags from the questionnaire. Conservative: when
    in doubt, protect the user (substitute a gentler action, never harm).

    Keyword-based inference over the free-text `health_limitations` (+ the
    `joint_pain` field). Every tag here must be one an ActionDef can carry so the
    gating in `_resolve_safe` can act on it — see bos/engines/02-knowledge-engine.md.
    """
    tags = set()
    jp = (getattr(response, 'joint_pain', '') or '').strip().lower()
    if jp and jp not in ('не', 'няма', 'no', 'none', '-'):
        tags.add('severe_joint_pain')
    hl = (getattr(response, 'health_limitations', '') or '').lower()

    def has(*keys):
        return any(k in hl for k in keys)

    if has('стави', 'колян', 'гръб', 'joint', 'knee', 'back'):
        tags.add('severe_joint_pain')
    if has('травма', 'контузия', 'счупен', 'операция', 'injury', 'surgery'):
        tags.add('acute_injury')
    if has('сърц', 'сърдечн', 'инфаркт', 'стенокарди', 'аритми', 'кръвно',
           'налягане', 'хипертони', 'heart', 'cardiac', 'hypertension'):
        tags.add('cardiac')
    if has('световъртеж', 'замайв', 'замая', 'вертиго', 'залитан', 'падан',
           'равновеси', 'dizzy', 'vertigo', 'balance'):
        tags.add('balance_issues')
    if has('астма', 'дишан', 'задух', 'бял дроб', 'хобб', 'respiratory',
           'asthma', 'copd', 'breath'):
        tags.add('respiratory')
    return tags


def _is_safe(action, tags):
    return not (set(action.contraindications or []) & tags)


def _resolve_safe(action, tags, by_slug):
    """The action itself if safe; else its first safe alternative; else None."""
    if _is_safe(action, tags):
        return action
    for alt_slug in (action.alternatives or []):
        alt = by_slug.get(alt_slug)
        if alt and _is_safe(alt, tags):
            return alt
    return None


def today_actions(response, today=None, n=3):
    """≥3 safe actions for today: undone core habits first, then a mission.
    Contraindicated actions are replaced by a safe alternative or dropped."""
    today = today or timezone.localdate()
    program, _ = UserProgram.objects.get_or_create(response=response)
    level = program.current_level
    done = set(ActionLog.objects.filter(
        response=response, date=today, status__in=ActionLog.COUNTS_AS_DONE,
    ).values_list('action__slug', flat=True))
    tags = user_contraindications(response)

    active = list(ActionDef.objects.filter(is_active=True))
    by_slug = {a.slug: a for a in active}
    core = [a for a in active if a.type == ActionDef.CORE]
    missions = [a for a in active if a.type == ActionDef.MISSION]
    rng = random.Random((response.pk or 0) + today.toordinal())
    rng.shuffle(missions)

    picked, seen = [], set()
    for a in core + missions:                 # core foundations first, then variety
        if a.slug in done:
            continue
        safe = _resolve_safe(a, tags, by_slug)  # gate/replace unsafe actions
        if safe is None or safe.slug in seen or safe.slug in done:
            continue
        seen.add(safe.slug)
        picked.append(safe)
        if len(picked) >= n:
            break
    return [card(a, level) for a in picked]
