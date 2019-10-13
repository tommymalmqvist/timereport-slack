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
    if round(float(hours)) > 8:
        return False
    elif round(float(hours)) < 0:
        return False
    else:
        return True


def validate_command_len(command: list) -> bool:
    if len(command) < 3 or len(command) > 4:
        return False
    return True
