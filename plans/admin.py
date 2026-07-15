from django.contrib import admin
from .models import QuestionnaireResponse, UserPlan, Feedback, StepCompletion


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'user', 'age', 'gender', 'main_goal', 'movement_level', 'energy_level', 'created_at']
    list_filter = ['main_goal', 'movement_level', 'gender', 'working_status']
    search_fields = ['ninety_day_goal', 'health_limitations']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(StepCompletion)
class StepCompletionAdmin(admin.ModelAdmin):
    list_display = ['id', 'response', 'category', 'step_text', 'completed_on', 'created_at']
    list_filter = ['category', 'completed_on']
    search_fields = ['step_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile_type', 'response', 'created_at']
    list_filter = ['profile_type']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'response', 'profile_type_display', 'age_display', 'main_goal_display',
        'clarity_score', 'usefulness_score', 'realistic_score',
        'would_use_again', 'would_pay', 'created_at',
    ]
    list_filter = ['would_use_again', 'would_pay', 'clarity_score']
    readonly_fields = [
        'created_at',
        'profile_type_display',
        'age_display', 'gender_display', 'height_weight_display',
        'working_status_display', 'living_status_display',
        'energy_display', 'sleep_display',
        'eating_display', 'evening_meal_display',
        'main_goal_display', 'movement_level_display', 'preferred_movement_display',
        'joint_pain_display', 'social_activity_display', 'hobby_display',
        'health_limitations_display', 'ninety_day_goal_display',
    ]
    ordering = ['-created_at']
    fieldsets = (
        ('Обратна връзка', {
            'fields': (
                'response',
                'clarity_score', 'usefulness_score', 'realistic_score',
                'would_use_again', 'would_pay', 'suggested_price',
                'most_useful_part', 'improvement_suggestion',
                'created_at',
            )
        }),
        ('Профил на участника', {
            'classes': ('collapse',),
            'fields': (
                'profile_type_display',
                'age_display', 'gender_display', 'height_weight_display',
                'working_status_display', 'living_status_display',
                'energy_display', 'sleep_display',
                'eating_display', 'evening_meal_display',
                'main_goal_display', 'movement_level_display', 'preferred_movement_display',
                'joint_pain_display', 'social_activity_display', 'hobby_display',
                'health_limitations_display', 'ninety_day_goal_display',
            ),
        }),
    )

    def _r(self, obj):
        return obj.response

    def profile_type_display(self, obj):
        try:
            return obj.response.plan.profile_type
        except Exception:
            return '–'
    profile_type_display.short_description = 'Тип профил'

    def age_display(self, obj):
        return f'{obj.response.age} г.'
    age_display.short_description = 'Възраст'

    def gender_display(self, obj):
        return obj.response.gender
    gender_display.short_description = 'Пол'

    def height_weight_display(self, obj):
        return f'{obj.response.height} см / {obj.response.weight} кг'
    height_weight_display.short_description = 'Ръст / тегло'

    def working_status_display(self, obj):
        return obj.response.working_status
    working_status_display.short_description = 'Работен статус'

    def living_status_display(self, obj):
        return obj.response.living_status
    living_status_display.short_description = 'С кого живее'

    def energy_display(self, obj):
        return f'{obj.response.energy_level}/5'
    energy_display.short_description = 'Ниво на енергия'

    def sleep_display(self, obj):
        return f'{obj.response.sleep_hours} ч.'
    sleep_display.short_description = 'Сън'

    def eating_display(self, obj):
        return obj.response.eating_frequency
    eating_display.short_description = 'Хранене'

    def evening_meal_display(self, obj):
        return obj.response.evening_meal_type
    evening_meal_display.short_description = 'Вечеря'

    def main_goal_display(self, obj):
        return obj.response.main_goal
    main_goal_display.short_description = 'Основна цел'

    def movement_level_display(self, obj):
        return obj.response.movement_level
    movement_level_display.short_description = 'Ниво на движение'

    def preferred_movement_display(self, obj):
        return obj.response.preferred_movement
    preferred_movement_display.short_description = 'Предпочитано движение'

    def joint_pain_display(self, obj):
        return obj.response.joint_pain
    joint_pain_display.short_description = 'Болки в ставите'

    def social_activity_display(self, obj):
        return obj.response.social_activity
    social_activity_display.short_description = 'Социална активност'

    def hobby_display(self, obj):
        return 'Да' if obj.response.has_hobby else 'Не'
    hobby_display.short_description = 'Хоби'

    def health_limitations_display(self, obj):
        return obj.response.health_limitations or '–'
    health_limitations_display.short_description = 'Здравословни ограничения'

    def ninety_day_goal_display(self, obj):
        return obj.response.ninety_day_goal
    ninety_day_goal_display.short_description = '90-дневна цел'
