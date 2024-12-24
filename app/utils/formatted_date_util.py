from datetime import datetime


def formatted_datetime():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def event_timestamp_tostring(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
