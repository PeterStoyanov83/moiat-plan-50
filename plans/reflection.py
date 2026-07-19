"""Daily reflection (AI Planner Engine — bos/engines/07-ai-planner-engine.md).

The morning payload ends with ONE gentle reflection question. Kept rule-based and
deterministic per day (so it doesn't change on refresh); the answer is stored so the
companion can learn over time. Tone: warm, calm, never demanding — same spirit as the
rest of the ritual.
"""
from django.utils import timezone
from .models import Reflection

# Gentle, open, non-judgemental. Never implies a "right" answer or a task.
QUESTIONS = [
    'Как се чувстваш след днешната стъпка?',
    'Кое беше най-хубавото в деня ти?',
    'За какво си благодарен днес?',
    'Какво ти донесе малко радост днес?',
    'Как е тялото ти днес — от какво има нужда?',
    'Кое ти беше лесно днес, а кое — по-трудно?',
    'Какво би искал да опиташ утре?',
    'Кой момент от деня искаш да запомниш?',
]


def question_for(response, today=None):
    """A stable question for this user+day (same on every refresh)."""
    today = today or timezone.localdate()
    seed = (getattr(response, 'pk', 0) or 0) + today.toordinal()
    return QUESTIONS[seed % len(QUESTIONS)]


def todays_reflection(response, today=None):
    today = today or timezone.localdate()
    return Reflection.objects.filter(response=response, date=today).first()


def save_reflection(response, answer, today=None, question=None):
    """Store (or update) today's reflection answer. Idempotent per day."""
    today = today or timezone.localdate()
    question = question or question_for(response, today)
    obj, _ = Reflection.objects.update_or_create(
        response=response, date=today,
        defaults={'question': question, 'answer': (answer or '').strip()},
    )
    return obj
