from datetime import datetime


def get_timestamp_text() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
