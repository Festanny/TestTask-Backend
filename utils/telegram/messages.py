from django.template.loader import render_to_string

from _project_ import constants
from .tasks import send_to_telegram


def send_order_notification_example(order):
    """
    Пример отправки уведомлений в телеграм
    Функцию нужно вызвать вручуную
    Для разных типов уведомлений предлагается создать свою, аналогичную функцию
    которая может принимать другие параметры, рендерить другой шаблон
    или отправлять сообщения в другой чат
    """
    message = render_to_string(
        'telegram/order_notification_example.html',
        context={"order": order}
    )
    send_to_telegram.delay(message, constants.TelegramChatKind.ORDER_NOTIFICATION_EXAMPLE.value)
