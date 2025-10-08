import logging
import traceback

from _project_ import constants


class TelegramHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        message = traceback.format_exc()

        from . import tasks
        kind = constants.TelegramChatKind.LOGGING_HANDLER.value
        tasks.send_to_telegram.delay(message, kind)
