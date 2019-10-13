from dateutil.parser import parse


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
