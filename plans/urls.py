from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('result/<int:plan_id>/', views.result, name='result'),
    path('download/<int:plan_id>/', views.download_pdf, name='download_pdf'),
    path('feedback/<int:response_id>/', views.feedback, name='feedback'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
]
