from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField


from . import serializers

from core import models


class FeedbackRequestCreateView(generics.CreateAPIView):
    serializer_class = serializers.FeedbackRequestSerializer
    permission_classes = (AllowAny,)


class SurveyView(
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Survey.objects.all()
    serializer_class = serializers.SurveySerializer
    http_method_names = ['get', 'post', 'patch']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class QuestionView(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    http_method_names = ['get', 'post', 'patch']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return serializers.QuestionUpdateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='next-question')
    def get_next_question(self, request, **kwargs):
        survey_id = request.query_params.get('survey_id')
        if not survey_id:
            return Response({'detail': 'Не указан survey_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            survey = models.Survey.objects.get(id=survey_id)
        except models.Survey.DoesNotExist:
            return Response({'detail': 'Опрос не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Получаем или создаём запись о прохождении
        user_survey, _ = models.UserSurvey.objects.get_or_create(user=request.user, survey=survey)

        # Определяем, какие вопросы уже пройдены
        answered_question_ids = user_survey.answers.values_list('question_id', flat=True)

        # Ищем первый ещё неотвеченный вопрос по порядку
        next_question = (
            survey.questions
            .exclude(id__in=answered_question_ids)
            .order_by('order')
            .first()
        )

        if not next_question:
            return Response({'detail': 'Опрос завершён'}, status=status.HTTP_200_OK)

        # Возвращаем сам вопрос и варианты ответов
        serializer = self.get_serializer(next_question)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAnswerView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.UserAnswer.objects.all()
    serializer_class = serializers.UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='survey-statistics')
    def survey_statistics(self, request, **kwargs):
        survey_id = request.query_params.get('survey_id')
        if not survey_id:
            return Response({"error": "Укажите survey_id в параметрах запроса"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            survey = models.Survey.objects.get(id=survey_id)
        except models.Survey.DoesNotExist:
            return Response({"error": "Опрос не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Подсчёт количества ответов на каждый вопрос
        answers_count = models.UserAnswer.objects.filter(
            question__survey=survey
        ).values('question__id', 'question__text').annotate(
            total_answers=Count('id')
        )

        # Популярные ответы для каждого вопроса
        popular_answers = models.UserAnswer.objects.filter(
            question__survey=survey
        ).values('question__id', 'selected_option__id', 'selected_option__text').annotate(
            votes=Count('id')
        ).order_by('question__id', '-votes')

        # Среднее время прохождения опроса
        user_surveys = models.UserSurvey.objects.filter(survey=survey, finished_at__isnull=False).annotate(
            duration=ExpressionWrapper(F('finished_at') - F('started_at'), output_field=DurationField())
        )
        avg_duration = user_surveys.aggregate(avg_time=Avg('duration'))['avg_time']

        return Response({
            "answers_count": list(answers_count),
            "popular_answers": list(popular_answers),
            "avg_completion_time": avg_duration.total_seconds() if avg_duration else None
        }, status=status.HTTP_200_OK)