from django.db import models


def get_default_bitrix_custom_fields_map():
    return {
        "auto": "UF_CRM_000000000",
        "shipping_date": "UF_CRM_000000000",
        "direction": "UF_CRM_000000000",
    }


class Settings(models.Model):
    bitrix_webhook_url = models.URLField(
        help_text="Оставьте пустым, чтобы отключить интеграцию с битрикс",
        blank=True,
        default=""
    )
    bitrix_lead_title_template = models.CharField(
        verbose_name="Шаблон заголовка лида в битрикс",
        help_text='Можно использовать просто строку, или шаблон django</br>'
                  'Пример: "Заявка на обратную связь от {{ phone }}"</br>'
                  'Можно использовать {% if ... %} {% endif %}</br>'
                  'Доступные переменные: first_name, last_name, phone, email',
        max_length=64
    )

    bitrix_custom_fields_map = models.JSONField(
        verbose_name="Маппинг полей",
        help_text='Формат: {"internal_field_key": "UF_CRM_1689233493499"}</br>'
                  'Где internal_field_key - внутреннее имя, UF_CRM_1689233493499 - имя поля в Битриксе</br>',
        default=get_default_bitrix_custom_fields_map
    )
