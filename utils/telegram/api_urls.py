_SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"


def get_send_message_url(token):
    return _SEND_MESSAGE_URL.format(token=token)
