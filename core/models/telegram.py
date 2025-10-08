from django.db import models

from _project_.constants import TelegramChatKind


class TelegramBotCredentials(models.Model):

    class Meta:
        verbose_name = "Данные от телеграм бота"
        verbose_name_plural = "Данные от телеграм ботов"

    KIND_CHOICES = (
        (TelegramChatKind.LOGGING_HANDLER.value, "Для логов"),
        (TelegramChatKind.ORDER_NOTIFICATION_EXAMPLE.value, "Для заказов"),
    )

    token = models.CharField(verbose_name="Токен", max_length=100)
    kind = models.CharField(verbose_name="Назначение", unique=True, choices=KIND_CHOICES, max_length=5)
    chat_id = models.CharField(verbose_name="Id чата", help_text="Куда отправлять", max_length=15)

    def __str__(self):
        return self.get_kind_display()
