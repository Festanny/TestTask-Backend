# MODELS

class Survey(models.Model):
    """Опрос"""
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title


class Question(models.Model):
    """Вопрос в опросе"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('survey', 'order')

    def __str__(self):
        return f"{self.order}. {self.text}"


class AnswerOption(models.Model):
    """Вариант ответа для вопроса"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('question', 'order')

    def __str__(self):
        return self.text


class UserSurvey(models.Model):
    """Прохождение опроса пользователем"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taken_surveys')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'survey')


class UserAnswer(models.Model):
    """Ответ пользователя на конкретный вопрос"""
    user_survey = models.ForeignKey(UserSurvey, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)


# VIEWS

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


# SERIALIZERS

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


# ROUTERS API

router = routers.DefaultRouter()
router.register(r'survey', views.SurveyView, basename='survey')
router.register(r'question', views.QuestionView, basename='question')
router.register(r'user-answer', views.UserAnswerView, basename='user-answer')

routers = [
    *router.urls,
]

urlpatterns = [
    path('', include("knox.urls")),
    *router.urls
]


# ADMIN

admin.site.register(models.Survey, admin.ModelAdmin)


class AnswerOptionInline(admin.TabularInline):
    model = models.AnswerOption
    extra = 0


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]


class UserAnswerInline(admin.TabularInline):
    model = models.UserAnswer
    extra = 0


@admin.register(models.UserSurvey)
class UserSurveyAdmin(admin.ModelAdmin):
    inlines = [UserAnswerInline]