from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SiteSettings(models.Model):
    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    robots = models.TextField("robots.txt", blank=True)
    favicon = models.ImageField("Favicon", upload_to="favicon", blank=True)
    extra_head_html = models.TextField(blank=True)
    extra_body_html = models.TextField(blank=True)

    @classmethod
    def get(cls):
        if not hasattr(cls, "_cached_obj"):
            cls._cached_obj = cls.objects.get()
        return cls._cached_obj

    def __str__(self):
        return "Настройки сайта"


class CompanyContacts(models.Model):
    email = models.EmailField(verbose_name="E-mail", blank=True)
    phone = models.CharField(verbose_name="Телефон", max_length=16, blank=True)
    requisites = models.TextField(verbose_name="Реквизиты", blank=True)

    address = models.CharField(verbose_name="Адрес", max_length=128, blank=True)
    address_html_code = models.TextField(verbose_name="HTML код для вставки карты", blank=True)

    class Meta:
        verbose_name = "Контакты компании"
        verbose_name_plural = "Контакты компании"

    def __str__(self):
        return "Контакты компании"


class ExtraFields(models.Model):
    class Meta:
        verbose_name = "Дополнительное поле"
        verbose_name_plural = "Дополнительные поля"

    key = models.CharField(verbose_name="Ключ", help_text="", max_length=20, unique=True)
    title = models.CharField(verbose_name="Заголовок", max_length=100, blank=True)
    text = models.TextField(verbose_name="Текст", blank=True)

    def __str__(self):
        return self.title or self.key


class FeedbackRequest(models.Model):
    first_name = models.CharField(max_length=64, verbose_name="Имя", blank=True)
    phone = models.CharField(max_length=24, verbose_name="Телефон", blank=True)
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заявка на обратную связь"
        verbose_name_plural = "Заявки на обратную связь"

    def __str__(self):
        return f'Заявка от {self.phone}'


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