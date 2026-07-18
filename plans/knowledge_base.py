"""Knowledge base loader and plan-section builders.

Reads the curated task pools in ``data/knowledge_base.json`` and turns them
into personalized plan sections. Movement and nutrition are leveled (the user
is mapped to level 1–3); social and finance are flat pools we sample from.

Selection is seeded by the response id, so a given plan is stable across page
reloads and PDF downloads, but varies from person to person.
"""
import json
import random
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / 'data' / 'knowledge_base.json'

# Maps the form's preferred_movement keys to display-friendly labels.
MOVEMENT_LABELS = {
    'ходене': 'Ходене',
    'колело': 'Колоездене',
    'плуване': 'Плуване',
    'гимнастика': 'Лека гимнастика',
    'йога': 'Йога / стречинг',
    'групови': 'Групови занимания',
    'друго': 'Любима активност',
}


@lru_cache(maxsize=1)
def load_kb():
    """Load and cache the knowledge base (parsed once per process)."""
    with open(DATA_PATH, encoding='utf-8') as f:
        return json.load(f)['knowledge_base']


def _rng(response, salt):
    """Deterministic RNG per response, so each section varies independently."""
    return random.Random((response.pk or 0) + salt)


def _preferred_list(response):
    raw = response.preferred_movement or ''
    return [MOVEMENT_LABELS.get(k.strip(), k.strip()) for k in raw.split(',') if k.strip()]


def movement_level_for(response):
    """Map the questionnaire to a movement level (1–3), erring gentle by default."""
    level = {'ниско': 1, 'леко': 2, 'умерено': 3, 'активно': 3}.get(response.movement_level, 1)
    if response.joint_pain == 'силно':
        level = 1
    elif response.joint_pain == 'умерено':
        level = min(level, 2)
    if response.energy_level <= 2:
        level = min(level, 2)
    return level


def nutrition_level_for(response):
    """Map eating habits and goal to a nutrition level (1–3)."""
    score = 1
    if response.eating_frequency in ('3', '4_5'):
        score += 1
    if response.main_goal in ('отслабване', 'баланс', 'енергия'):
        score += 1
    return min(score, 3)


def build_movement_plan(response):
    kb = load_kb()
    level = movement_level_for(response)
    node = kb['movement']['levels'][str(level)]
    tasks = list(node['tasks'])
    _rng(response, 1).shuffle(tasks)

    preferred = _preferred_list(response)
    days = [f'Ниво: {node["name"]}', '']
    task_i = 0
    for day in range(1, 8):
        if day == 4:
            days.append('Ден 4: Почивка и леко разтягане')
        elif day in (2, 6) and preferred:
            move = preferred[day % len(preferred)]
            days.append(f'Ден {day}: {move} – по ваш избор')
        else:
            days.append(f'Ден {day}: {tasks[task_i % len(tasks)]}')
            task_i += 1
    return '\n'.join(days)


def build_nutrition_plan(response):
    kb = load_kb()
    level = nutrition_level_for(response)
    node = kb['nutrition']['levels'][str(level)]

    lines = [f'Ниво: {node["name"]}', '']
    lines += [f'• {t}' for t in node['tasks']]
    lines += ['', 'Златни правила:']
    lines += [f'• {r}' for r in kb['nutrition']['golden_rules']]
    return '\n'.join(lines)


def build_social_plan(response):
    kb = load_kb()
    tasks = _rng(response, 2).sample(kb['social']['tasks'], 4)
    return 'Изберете по една задача на всеки няколко дни:\n' + '\n'.join(f'• {t}' for t in tasks)


def build_financial_habit(response):
    kb = load_kb()
    tasks = _rng(response, 3).sample(kb['finance']['tasks'], 4)
    return 'Малки финансови навици за тази седмица:\n' + '\n'.join(f'• {t}' for t in tasks)
