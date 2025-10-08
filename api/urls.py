from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'survey', views.SurveyView, basename='survey')
router.register(r'question', views.QuestionView, basename='question')
router.register(r'user-answer', views.UserAnswerView, basename='user-answer')

routers = [
    *router.urls,
]

urlpatterns = [
    path('', include("knox.urls")),
    path('feedback-request/', views.FeedbackRequestCreateView.as_view(), name="api-feedbackrequest-list"),
    *router.urls
]
