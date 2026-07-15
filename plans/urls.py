from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('ritual/', views.ritual, name='ritual'),
    path('ritual/done/', views.step_done, name='step_done'),
    path('ritual/swap/', views.step_swap, name='step_swap'),
    path('progress/', views.progress, name='progress'),
    path('result/<int:plan_id>/', views.result, name='result'),
    path('download/<int:plan_id>/', views.download_pdf, name='download_pdf'),
    path('feedback/<int:response_id>/', views.feedback, name='feedback'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
]
