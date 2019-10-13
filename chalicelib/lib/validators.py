from dateutil.parser import parse
from datetime import datetime, timedelta


def validate_reason(reason: str, reasons: tuple) -> bool:
    """Validates a given reason for an event
    :param reason: str
    :param reasons: tuple
    :return: bool
    """
    if reason in reasons:
        return True
    else:
        return False


def validate_hours(hours: str) -> bool:
    try:
        if round(float(hours)) > 8:
            return False
        elif round(float(hours)) < 0:
            return False
        else:
            return True
    except ValueError:
        return False


def validate_date(date: str) -> bool:
    if not parse(date, fuzzy=False):
        return False
    else:
        return True


def validate_date_range(start: str, stop: str, format_str: str) -> bool:

    # create datetime objects
    date_obj_start = datetime.strptime(start, format_str)
    date_obj_stop = datetime.strptime(stop, format_str)

    # start has to be before stop
    if date_obj_start > date_obj_stop:
        return False

    # TODO: how long a range should we allow?
    counter = 0
    for d in date_range(date_obj_start, date_obj_stop):
        counter += 1

    if counter > 40:
        return False

    return True


def date_range(start_date, stop_date):
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta

