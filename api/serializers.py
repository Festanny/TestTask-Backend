from django.utils import timezone
from django.contrib.redirects.models import Redirect
from rest_framework import serializers

from core import models


class TextPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TextPage
        fields = ("name", "content", "slug", "show_in_sitemap", "og_title",
                  "og_description", "og_type", "og_type_pb_time", "og_type_author",
                  "seo_h1", "seo_title", "seo_description", "seo_keywords",)


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ("site", "old_path", "new_path")


class FeedbackRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FeedbackRequest
        fields = ("first_name", "phone", "comment")


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnswerOption
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True)

    class Meta:
        model = models.Question
        fields = ['id', 'survey', 'text', 'order', 'options']

    def create(self, validated_data):
        # Извлекаем вложенные данные (варианты ответов)
        options_data = validated_data.pop('options', [])

        # Создаём вопрос
        question = models.Question.objects.create(**validated_data)

        # Создаём варианты ответов, если они есть
        for option_data in options_data:
            models.AnswerOption.objects.create(question=question, **option_data)

        return question


class QuestionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Question
        fields = '__all__'


class SurveySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.Survey
        fields = '__all__'
        read_only_fields = ['author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserAnswer
        fields = ['id', 'question', 'selected_option']

    def validate(self, attrs):
        """Проверяем, что пользователь не ответил на этот вопрос ранее в рамках опроса"""
        user = self.context['request'].user
        question = attrs['question']
        survey = question.survey

        # Получаем или создаём UserSurvey
        user_survey, _ = models.UserSurvey.objects.get_or_create(user=user, survey=survey)

        # Проверяем, есть ли уже ответ на этот вопрос
        if models.UserAnswer.objects.filter(user_survey=user_survey, question=question).exists():
            raise serializers.ValidationError("Вы уже ответили на этот вопрос.")

        attrs['user_survey'] = user_survey
        return attrs

    def create(self, validated_data):
        user_survey = validated_data.pop('user_survey')

        # Создаём ответ
        user_answer = models.UserAnswer.objects.create(user_survey=user_survey, **validated_data)

        # Проверяем, остались ли непройденные вопросы
        answered_question_ids = user_survey.answers.values_list('question_id', flat=True)
        remaining_questions = user_survey.survey.questions.exclude(id__in=answered_question_ids)

        if not remaining_questions.exists():
            user_survey.finished_at = timezone.now()
            user_survey.save()

        return user_answer