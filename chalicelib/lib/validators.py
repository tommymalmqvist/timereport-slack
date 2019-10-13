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


def validate_command_len(command: list) -> bool:
    """
    Force length of command to be of len 3 or 4
    :param command: list
    :return: bool
    """
    if len(command) == 3 or len(command) == 4:
        return True
    else:
        return False
