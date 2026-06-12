from django.contrib import admin
from .models import QuestionnaireResponse, UserPlan, Feedback


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'age', 'gender', 'main_goal', 'movement_level', 'energy_level', 'created_at']
    list_filter = ['main_goal', 'movement_level', 'gender', 'working_status']
    search_fields = ['ninety_day_goal', 'health_limitations']
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
        'id', 'response', 'clarity_score', 'usefulness_score',
        'realistic_score', 'would_use_again', 'would_pay', 'created_at',
    ]
    list_filter = ['would_use_again', 'would_pay', 'clarity_score']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
