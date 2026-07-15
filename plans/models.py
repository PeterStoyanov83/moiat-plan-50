from django.conf import settings
from django.db import models


class QuestionnaireResponse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='questionnaire_responses', verbose_name='Потребител',
    )
    first_name = models.CharField(
        max_length=50, blank=True, verbose_name='Име'
    )
    age = models.IntegerField(verbose_name='Възраст')
    gender = models.CharField(max_length=20, verbose_name='Пол')
    height = models.IntegerField(verbose_name='Ръст (см)')
    weight = models.IntegerField(verbose_name='Тегло (кг)')
    working_status = models.CharField(max_length=50, verbose_name='Работен статус')
    living_status = models.CharField(max_length=50, verbose_name='С кого живеете')
    energy_level = models.IntegerField(verbose_name='Ниво на енергия (1-5)')
    sleep_hours = models.IntegerField(verbose_name='Часове сън')
    health_limitations = models.TextField(blank=True, verbose_name='Здравословни ограничения')
    eating_frequency = models.CharField(max_length=50, verbose_name='Честота на хранене')
    evening_meal_type = models.CharField(max_length=50, verbose_name='Вечерно хранене')
    main_goal = models.CharField(max_length=50, verbose_name='Основна цел')
    movement_level = models.CharField(max_length=50, verbose_name='Ниво на движение')
    preferred_movement = models.CharField(max_length=200, verbose_name='Предпочитано движение')
    joint_pain = models.CharField(max_length=20, verbose_name='Болки в ставите')
    social_activity = models.CharField(max_length=50, verbose_name='Социална активност')
    has_hobby = models.BooleanField(verbose_name='Има хоби')
    ninety_day_goal = models.TextField(verbose_name='90-дневна цел')
    consent_given = models.BooleanField(
        default=False, verbose_name='Съгласие за обработка на лични данни'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отговор от въпросник'
        verbose_name_plural = 'Отговори от въпросник'

    def __str__(self):
        return f'Отговор #{self.pk} – {self.age} г., {self.created_at.strftime("%d.%m.%Y")}'


class UserPlan(models.Model):
    response = models.OneToOneField(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='plan'
    )
    profile_type = models.CharField(max_length=100, verbose_name='Тип профил')
    profile_description = models.TextField(verbose_name='Описание на профила')
    nutrition_plan = models.TextField(verbose_name='Хранителен план')
    movement_plan = models.TextField(verbose_name='План за движение')
    habits_plan = models.TextField(verbose_name='Ежедневни навици')
    financial_habit = models.TextField(verbose_name='Финансов навик')
    social_plan = models.TextField(verbose_name='Социален план')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Личен план'
        verbose_name_plural = 'Лични планове'

    def __str__(self):
        return f'План #{self.pk} – {self.profile_type}'


class Feedback(models.Model):
    response = models.ForeignKey(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='feedbacks'
    )
    clarity_score = models.IntegerField(verbose_name='Яснота (1-5)')
    usefulness_score = models.IntegerField(verbose_name='Полезност (1-5)')
    realistic_score = models.IntegerField(verbose_name='Реалистичност (1-5)')
    would_use_again = models.BooleanField(verbose_name='Би използвал отново')
    would_pay = models.BooleanField(verbose_name='Би платил')
    suggested_price = models.CharField(max_length=50, blank=True, verbose_name='Предложена цена')
    most_useful_part = models.TextField(blank=True, verbose_name='Най-полезната част')
    improvement_suggestion = models.TextField(blank=True, verbose_name='Предложение за подобрение')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Обратна връзка'
        verbose_name_plural = 'Обратни връзки'

    def __str__(self):
        return f'Обратна връзка #{self.pk} за отговор #{self.response_id}'


class StepCompletion(models.Model):
    """One completed daily step. The daily ritual serves steps from the
    knowledge base one at a time; each 'Направих го' writes a row here.
    This powers today's count, streaks, and rotation (avoid repeats)."""
    response = models.ForeignKey(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='step_completions'
    )
    category = models.CharField(max_length=20, verbose_name='Категория')
    step_text = models.TextField(verbose_name='Стъпка')
    completed_on = models.DateField(verbose_name='Дата')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Изпълнена стъпка'
        verbose_name_plural = 'Изпълнени стъпки'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['response', 'completed_on'])]

    def __str__(self):
        return f'{self.step_text} ({self.completed_on})'
