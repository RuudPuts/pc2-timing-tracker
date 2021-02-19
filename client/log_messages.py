from datetime import datetime

log_messages = []


def log_message(message: str):
    message = "[{}] {}".format(datetime.now().strftime("%H:%M:%S"), message)

    print(message)

    log_messages.append(message)
