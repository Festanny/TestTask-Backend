import enum

from accounts.constants import *
from api.constants import *
from core.constants import *

TELEGRAM_TIMEOUT = 3


class TelegramChatKind(str, enum.Enum):
    LOGGING_HANDLER = "logs"
    ORDER_NOTIFICATION_EXAMPLE = "order"
