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


# ---------------------------------------------------------------------------
# Habit Evolution Engine (see design/HABIT_ENGINE_SPEC.md)
# Verified, level-based behavioural transformation. User-scoped rows anchor to
# QuestionnaireResponse (same anchor as StepCompletion — works anon + logged-in).
# ---------------------------------------------------------------------------

class Level(models.Model):
    """Static program-level config (1..20). Seeded in migration 0007."""
    number = models.PositiveSmallIntegerField(unique=True, verbose_name='Ниво')
    min_days = models.PositiveSmallIntegerField(default=14, verbose_name='Минимум дни')
    consistency_req = models.PositiveSmallIntegerField(verbose_name='Постоянство %')
    completion_req = models.PositiveSmallIntegerField(verbose_name='Завършеност %')
    core_habit_req = models.PositiveSmallIntegerField(verbose_name='Основни навици %')

    class Meta:
        ordering = ['number']
        verbose_name = 'Ниво'
        verbose_name_plural = 'Нива'

    def __str__(self):
        return f'Ниво {self.number}'


class ActionDef(models.Model):
    """The action library — core habits + growth missions, with verification."""
    CORE, MISSION = 'core_habit', 'growth_mission'
    TYPE_CHOICES = [(CORE, 'Основен навик'), (MISSION, 'Мисия за растеж')]
    VERIF_CHOICES = [
        ('sensor', 'Сензор'), ('timer', 'Таймер'), ('location', 'Локация'),
        ('photo_ai', 'Снимка/AI'), ('confirm', 'Потвърждение'),
    ]
    slug = models.SlugField(max_length=64, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=CORE)
    category = models.CharField(max_length=20)  # movement|nutrition|sleep|hydration|social|mind
    title = models.CharField(max_length=200)
    why = models.TextField(blank=True)
    verification_type = models.CharField(max_length=20, choices=VERIF_CHOICES, default='confirm')
    verification_source = models.CharField(max_length=64, blank=True)  # healthkit/google_fit
    metric = models.CharField(max_length=32, blank=True)  # steps, minutes...
    level_scaling = models.JSONField(default=dict, blank=True)  # {"1":2000,"5":5000,...}
    # Constitution: "no action without metadata" — safety + adaptation fields.
    difficulty = models.PositiveSmallIntegerField(default=1)  # 1 (gentle) .. 5 (demanding)
    duration_min = models.PositiveSmallIntegerField(null=True, blank=True)  # typical minutes
    contraindications = models.JSONField(default=list, blank=True)   # e.g. ["severe_joint_pain"]
    weather_adaptations = models.JSONField(default=dict, blank=True)  # {"rain": "indoor_march"}
    alternatives = models.JSONField(default=list, blank=True)         # fallback ActionDef slugs
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'

    def target_for_level(self, level: int):
        """Nearest defined target at or below `level` from level_scaling."""
        if not self.level_scaling:
            return None
        defined = sorted((int(k), v) for k, v in self.level_scaling.items())
        chosen = None
        for lv, val in defined:
            if lv <= level:
                chosen = val
        return chosen if chosen is not None else defined[0][1]

    def __str__(self):
        return f'{self.title} [{self.slug}]'


class UserProgram(models.Model):
    """One user's position in the 20-level program."""
    response = models.OneToOneField(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='program'
    )
    current_level = models.PositiveSmallIntegerField(default=1)
    level_started_on = models.DateField(auto_now_add=True)
    extended_days = models.PositiveSmallIntegerField(default=0)
    recovery_until = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Програма на потребител'
        verbose_name_plural = 'Програми на потребители'

    def __str__(self):
        return f'Програма #{self.pk} — ниво {self.current_level}'


class ActionLog(models.Model):
    """One attempt/completion of an action, with verification outcome."""
    PENDING, VERIFIED, UNVERIFIED, CONFIRMED, REJECTED = (
        'pending', 'verified', 'unverified', 'confirmed', 'rejected')
    STATUS_CHOICES = [
        (PENDING, 'Изчаква'), (VERIFIED, 'Потвърдено (сензор)'),
        (UNVERIFIED, 'Непотвърдено'), (CONFIRMED, 'Потвърдено (доверие)'),
        (REJECTED, 'Отхвърлено'),
    ]
    response = models.ForeignKey(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='action_logs'
    )
    action = models.ForeignKey(ActionDef, null=True, on_delete=models.SET_NULL)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    verification_type = models.CharField(max_length=20, blank=True)
    claimed_value = models.FloatField(null=True, blank=True)
    measured_value = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    COUNTS_AS_DONE = {VERIFIED, CONFIRMED}

    class Meta:
        verbose_name = 'Дневник на действие'
        verbose_name_plural = 'Дневник на действия'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['response', 'date'])]

    def __str__(self):
        return f'{self.action_id} {self.date} → {self.status}'


class HabitStability(models.Model):
    """Rolling stability (0..100) per category or action slug."""
    response = models.ForeignKey(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='habit_stabilities'
    )
    key = models.CharField(max_length=40)  # category or action slug
    stability = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Стабилност на навик'
        verbose_name_plural = 'Стабилности на навици'
        unique_together = [('response', 'key')]

    def __str__(self):
        return f'{self.key}: {self.stability}%'


class TreeState(models.Model):
    """Derived Living Tree state (cache), recomputed on activity. Feeds the
    front-end engine's completedActions/level/health/dormant inputs."""
    response = models.OneToOneField(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='tree_state'
    )
    age = models.PositiveIntegerField(default=0)          # completed actions total
    growth_stage = models.PositiveSmallIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)   # 1..20
    health = models.PositiveSmallIntegerField(default=100)
    branches = models.PositiveIntegerField(default=0)
    leaves = models.PositiveIntegerField(default=0)
    flowers = models.PositiveIntegerField(default=0)
    dormant = models.BooleanField(default=False)
    last_activity = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Състояние на дървото'
        verbose_name_plural = 'Състояния на дърветата'

    def __str__(self):
        return f'Дърво #{self.pk} — ниво {self.level}, здраве {self.health}'


class DailyAssignment(models.Model):
    """The core + mission actions offered to a user on a given day."""
    CORE, MISSION = 'core', 'mission'
    SLOT_CHOICES = [(CORE, 'Основен навик'), (MISSION, 'Мисия')]
    response = models.ForeignKey(
        QuestionnaireResponse, on_delete=models.CASCADE, related_name='daily_assignments'
    )
    date = models.DateField()
    action = models.ForeignKey(ActionDef, null=True, on_delete=models.SET_NULL)
    slot = models.CharField(max_length=10, choices=SLOT_CHOICES, default=CORE)

    class Meta:
        verbose_name = 'Дневно назначение'
        verbose_name_plural = 'Дневни назначения'
        unique_together = [('response', 'date', 'action')]
        indexes = [models.Index(fields=['response', 'date'])]

    def __str__(self):
        return f'{self.date} {self.slot}: {self.action_id}'
