"""AI daily companion — Claude picks today's one step and frames it warmly.

This is an *optional* layer over the rule-based step engine. When an
``ANTHROPIC_API_KEY`` is configured, Claude chooses the single most fitting step
for the day from the eligible candidates and writes one warm Bulgarian line
("днес направи само това"). On any problem — no key, network error, timeout,
bad output — it silently falls back to the deterministic ``offer_step`` engine,
so the ritual never breaks.

Model: Haiku 4.5 — a tiny pick + one-sentence task that runs on page load, so
speed and cost matter (it does not accept ``effort``/``thinking``; we don't send
them). Structured output via ``output_config.format`` returns ``{index, message}``.
"""
import json
import logging
import os
from functools import lru_cache

from django.utils import timezone

logger = logging.getLogger(__name__)

# Haiku is the right tier for a fast per-request pick; override via env if needed.
MODEL = os.environ.get('AI_COMPANION_MODEL', 'claude-haiku-4-5')
TIMEOUT = float(os.environ.get('AI_COMPANION_TIMEOUT', '6'))

_SCHEMA = {
    'type': 'object',
    'properties': {
        'index': {'type': 'integer'},
        'message': {'type': 'string'},
        'reflection': {'type': 'string'},
    },
    'required': ['index', 'message', 'reflection'],
    'additionalProperties': False,
}

_SYSTEM = (
    'Ти си топъл, спокоен ежедневен спътник в приложение за всеки, който иска да живее по-здравословно. '
    'Философията е „Една стъпка. Всеки ден.“ — човекът прави само по една малка стъпка. '
    'От дадения списък избери ЕДНА стъпка, която е най-подходяща за днес, и напиши '
    'едно кратко, топло изречение на български, което нежно подканя човека да я направи. '
    'Състави и един мек, отворен въпрос за размисъл в края на деня (никога за нива или числа). '
    'Ако са дадени последни споделяния от човека, съобрази тона нежно с тях. '
    'Без натиск, без списъци, без емоджи. Върни само JSON: '
    '{"index": <номер>, "message": <изречение>, "reflection": <въпрос>}.'
)


def enabled():
    """The companion is active only when an API key is present."""
    return bool(os.environ.get('ANTHROPIC_API_KEY'))


@lru_cache(maxsize=1)
def _client():
    import anthropic
    return anthropic.Anthropic(timeout=TIMEOUT, max_retries=1)


def _ai_choose(response, candidates):
    """Ask Claude to pick an index + write a warm line + a reflection question,
    learning gently from recent reflections. Returns (index, message, reflection) or None."""
    try:
        from .reflection import recent_answers
        name = (response.first_name or '').strip()
        listing = '\n'.join(f'{i}. [{c["category"]}] {c["text"]}' for i, c in enumerate(candidates))
        recent = recent_answers(response)
        context = ''
        if recent:
            context = ('Последни споделяния от човека (за контекст, ползвай нежно): '
                       + ' | '.join(recent) + '\n')
        user = (
            f'Име: {name or "потребителят"}\n'
            f'Възможни стъпки за днес:\n{listing}\n'
            f'{context}\n'
            'Избери индекса на най-подходящата една стъпка, напиши едно топло изречение '
            'и състави един мек въпрос за размисъл.'
        )
        resp = _client().messages.create(
            model=MODEL,
            max_tokens=300,
            system=_SYSTEM,
            messages=[{'role': 'user', 'content': user}],
            output_config={'format': {'type': 'json_schema', 'schema': _SCHEMA}},
        )
        text = next(b.text for b in resp.content if b.type == 'text')
        data = json.loads(text)
        idx, msg = int(data['index']), str(data['message']).strip()
        reflection = str(data.get('reflection', '')).strip() or None
        if 0 <= idx < len(candidates) and msg:
            return idx, msg, reflection
    except Exception as e:  # any failure → fall back, never break the ritual
        logger.warning('AI companion unavailable, using rule-based engine: %s', e)
    return None


def pick_opening_step(response):
    """Choose the day's opening step, a warm line, and a reflection question.

    Returns ``(step_dict_or_None, message_or_None, reflection_or_None)``. Uses Claude
    when enabled, otherwise the deterministic engine. ``message``/``reflection`` are
    None unless the AI wrote them (caller falls back to the rule-based reflection pool).
    """
    # Imported here to avoid any import cycle with step_engine.
    from .step_engine import offer_step, eligible_steps, _completed_today_texts

    today = timezone.localdate()
    done = _completed_today_texts(response, today)
    candidates = [s for s in eligible_steps(response) if s['text'] not in done]
    if not candidates:
        return None, None, None

    if enabled():
        chosen = _ai_choose(response, candidates[:8])
        if chosen:
            idx, message, reflection = chosen
            return candidates[idx], message, reflection

    return offer_step(response, today=today), None, None
