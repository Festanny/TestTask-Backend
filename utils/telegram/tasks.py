import requests

from _project_.celery import app
from _project_ import constants

from . import api_urls


@app.task()
def send_to_telegram(message, chat_kind):
    from core import models

    tg_credentials = models.TelegramBotCredentials.objects.get(kind=chat_kind)

    url = api_urls.get_send_message_url(tg_credentials.token)
    chat_id = tg_credentials.chat_id

    requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        },
        timeout=constants.TELEGRAM_TIMEOUT
    )
