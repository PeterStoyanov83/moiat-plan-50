from datetime import date

from django.test import TestCase

from .models import QuestionnaireResponse, StepCompletion
from . import step_engine as se


def make_response(**overrides):
    data = dict(
        first_name='Петър', age=62, gender='жена', height=165, weight=80,
        working_status='пенсионер', living_status='сам', energy_level=3, sleep_hours=7,
        health_limitations='', eating_frequency='3', evening_meal_type='лека',
        main_goal='баланс', movement_level='леко', preferred_movement='ходене',
        joint_pain='не', social_activity='средна', has_hobby=False,
        ninety_day_goal='повече енергия', consent_given=True,
    )
    data.update(overrides)
    return QuestionnaireResponse.objects.create(**data)


class StepEngineTests(TestCase):
    def test_eligible_steps_span_all_categories(self):
        r = make_response()
        cats = {s['category'] for s in se.eligible_steps(r)}
        self.assertEqual(cats, {se.MOVEMENT, se.NUTRITION, se.SOCIAL, se.FINANCE})

    def test_social_profile_offers_social_first(self):
        # social_activity 'ниска' -> profile "Социално активиране"
        r = make_response(social_activity='ниска')
        first = se.eligible_steps(r)[0]
        self.assertEqual(first['category'], se.SOCIAL)

    def test_level_controls_movement_pool(self):
        low = make_response(movement_level='ниско', energy_level=2)   # level 1
        high = make_response(movement_level='активно', joint_pain='не')  # level 3
        low_texts = {s['text'] for s in se.eligible_steps(low) if s['category'] == se.MOVEMENT}
        high_texts = {s['text'] for s in se.eligible_steps(high) if s['category'] == se.MOVEMENT}
        self.assertIn('10 минути ходене', low_texts)          # a level-1 task
        self.assertNotIn('10 минути ходене', high_texts)      # not in level-3 pool

    def test_offer_skips_completed_today(self):
        r = make_response()
        step = se.offer_step(r)
        self.assertIsNotNone(step)
        se.mark_done(r, step['text'], step['category'])
        remaining = se.offer_step(r)
        self.assertNotEqual(remaining['text'], step['text'])

    def test_swap_excludes_current(self):
        r = make_response()
        step = se.offer_step(r)
        other = se.offer_step(r, exclude=[step['text']])
        self.assertNotEqual(other['text'], step['text'])

    def test_mark_done_is_idempotent_per_day(self):
        r = make_response()
        today = date(2026, 7, 15)
        self.assertTrue(se.mark_done(r, '10 минути ходене', se.MOVEMENT, today=today))
        self.assertFalse(se.mark_done(r, '10 минути ходене', se.MOVEMENT, today=today))
        self.assertEqual(StepCompletion.objects.filter(response=r).count(), 1)

    def test_progress_counts_and_streak(self):
        r = make_response()
        t = date(2026, 7, 15)
        y = date(2026, 7, 14)
        se.mark_done(r, 'A', se.SOCIAL, today=y)
        se.mark_done(r, 'B', se.SOCIAL, today=t)
        se.mark_done(r, 'C', se.FINANCE, today=t)
        prog = se.today_progress(r, today=t)
        self.assertEqual(prog['done_today'], 2)
        self.assertEqual(prog['streak'], 2)
