import datetime


now = datetime.datetime.now


def utc_now():
    return now(datetime.timezone.utc).timestamp()

