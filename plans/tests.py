from datetime import date
from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse

from .models import QuestionnaireResponse, StepCompletion, UserPlan
from . import step_engine as se
from . import ai_companion


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


class RitualFlowTests(TestCase):
    """End-to-end: interview -> session -> ritual -> done/swap endpoints."""

    FORM = dict(
        first_name='Петър', age=62, gender='жена', height=165, weight=80,
        working_status='пенсионер', living_status='с_партньор',
        energy_level='3', sleep_hours='7', health_limitations='',
        eating_frequency='3', evening_meal_type='лека', main_goal='баланс',
        movement_level='леко', preferred_movement=['ходене', 'плуване'],
        joint_pain='не', social_activity='средна', has_hobby='',
        ninety_day_goal='повече енергия', consent_given='on',
    )

    def test_questionnaire_redirects_to_ritual_and_sets_session(self):
        c = Client()
        resp = c.post(reverse('questionnaire'), self.FORM)
        self.assertRedirects(resp, reverse('ritual'))
        self.assertIn('response_id', c.session)
        self.assertEqual(UserPlan.objects.count(), 1)   # full plan still built

    def test_ritual_shows_a_step_then_done_offers_next(self):
        c = Client()
        c.post(reverse('questionnaire'), self.FORM)
        r = c.get(reverse('ritual'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Петър')                 # greeting personalized

        # eligible steps exist for this session's response
        resp_obj = QuestionnaireResponse.objects.get()
        step = se.eligible_steps(resp_obj)[0]

        done = c.post(reverse('step_done'), {'text': step['text'], 'category': step['category']})
        self.assertEqual(done.status_code, 200)
        data = done.json()
        self.assertIn('choices', data)                       # next set of options
        self.assertEqual(data['progress']['done_today'], 1)
        texts = [s['text'] for s in data['choices']]
        self.assertNotIn(step['text'], texts)                # done step not re-offered
        self.assertLessEqual(len(data['choices']), 3)

    def test_ritual_without_session_redirects_to_questionnaire(self):
        c = Client()
        self.assertRedirects(c.get(reverse('ritual')), reverse('questionnaire'))

    def test_swap_returns_different_step(self):
        c = Client()
        c.post(reverse('questionnaire'), self.FORM)
        resp_obj = QuestionnaireResponse.objects.get()
        step = se.eligible_steps(resp_obj)[0]
        sw = c.post(reverse('step_swap'), {'exclude': step['text']})
        self.assertEqual(sw.status_code, 200)
        self.assertNotEqual(sw.json()['next']['text'], step['text'])

    def test_progress_page_renders_after_a_step(self):
        c = Client()
        c.post(reverse('questionnaire'), self.FORM)
        resp_obj = QuestionnaireResponse.objects.get()
        step = se.eligible_steps(resp_obj)[0]
        c.post(reverse('step_done'), {'text': step['text'], 'category': step['category']})
        r = c.get(reverse('progress'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Твоят напредък')
        self.assertContains(r, step['text'])          # shows in "Последни крачки"

    def test_progress_without_session_redirects(self):
        self.assertRedirects(Client().get(reverse('progress')), reverse('questionnaire'))


class AICompanionTests(TestCase):
    def test_falls_back_to_engine_when_disabled(self):
        r = make_response()
        with mock.patch.object(ai_companion, 'enabled', return_value=False):
            step, message = ai_companion.pick_opening_step(r)
        self.assertIsNotNone(step)
        self.assertIn(step['category'], {se.MOVEMENT, se.NUTRITION, se.SOCIAL, se.FINANCE})
        self.assertIsNone(message)   # no AI line when disabled

    def test_uses_ai_choice_when_enabled(self):
        r = make_response()
        with mock.patch.object(ai_companion, 'enabled', return_value=True), \
             mock.patch.object(ai_companion, '_ai_choose', return_value=(0, 'Днес една малка крачка.')):
            step, message = ai_companion.pick_opening_step(r)
        # index 0 of the candidate list, with the AI's warm line
        candidates = [s for s in se.eligible_steps(r)]
        self.assertEqual(step['text'], candidates[0]['text'])
        self.assertEqual(message, 'Днес една малка крачка.')


class GoogleAccountTests(TestCase):
    """Signed-in users own their response and get it back on any device."""

    def _user(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user(
            username='u1', email='m@example.com', first_name='Мария')

    def test_questionnaire_prefills_name_from_google_profile(self):
        c = Client()
        c.force_login(self._user())
        r = c.get(reverse('questionnaire'))
        self.assertContains(r, 'value="Мария"')       # first_name prefilled

    def test_response_is_tied_to_user_and_loads_cross_device(self):
        user = self._user()
        form = RitualFlowTests.FORM
        # device A: sign in, complete interview
        a = Client(); a.force_login(user)
        a.post(reverse('questionnaire'), form)
        resp = QuestionnaireResponse.objects.get()
        self.assertEqual(resp.user, user)              # owned by the account

        # device B: fresh session, same account -> ritual loads their response
        b = Client(); b.force_login(user)
        self.assertEqual(b.get(reverse('ritual')).status_code, 200)

    def test_login_claims_anonymous_session_response(self):
        user = self._user()
        c = Client()
        c.post(reverse('questionnaire'), RitualFlowTests.FORM)   # anonymous
        resp = QuestionnaireResponse.objects.get()
        self.assertIsNone(resp.user)
        c.force_login(user)
        c.get(reverse('ritual'))                                 # triggers claim
        resp.refresh_from_db()
        self.assertEqual(resp.user, user)
