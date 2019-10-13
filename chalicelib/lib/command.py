from chalice import Chalice

from app import SECRET, REASONS, API_URL
from chalicelib.lib import api
from chalicelib.lib.security import verify_token
from chalicelib.lib.slack import slack_payload_extractor, slack_responder
from chalicelib.lib.validators import validate_hours, validate_reason, validate_date


def command_handler(app: Chalice):
    """Takes chalice app, extracts headers and request
    validates token and sends extracted data
    to the correct function handler
    """

    # store headers, request
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()

    # extract payload from request
    payload: dict = slack_payload_extractor(request)
    response_url: str = payload["response_url"][0]

    # verify token
    if not verify_token(headers, request, SECRET):
        slack_responder(response_url, "Slack signing secret not valid")
        return ""

    # store command input, user_id and action
    try:
        command: tuple = tuple(payload["text"][0].split())
        user_id: str = payload["user_id"][0]
        action: str = command[0]
    except KeyError:
        slack_responder(response_url, help_menu())
        return ""

    # begin matching action
    if action == "add":
        slack_responder(response_url, add(command, user_id))
        return ""

    elif action == "list":
        slack_responder(response_url, ls(command, user_id))
        return ""

    elif action == "delete":
        slack_responder(response_url, delete(command, user_id))
        return ""

    elif action == "lock":
        slack_responder(response_url, lock(command, user_id))
        return ""

    elif action == "help":
        slack_responder(response_url, help_menu())
        return ""


def add(command: tuple, user_id: str) -> str:
    """Checks if reason and date are valid strings

    If date is range ("2019-12-28:2020-01-03") it will
    test if range is valid

    :param command: list containing:
        command[0] = action: str "add"
        command[1] = reason: str ["vab", "sick", "intern"]
        command[2] = date: str ["2019-12-28", "today", "today 8", "today 24", "2019-12-28:2020-01-03"]
        command[3] = hours: OPTIONAL str: - hours is optional and defaults to 8 if not given
    :param user_id: str: user_id
    :param response_url: str: callback

    :return str: sent to slack_responder

    Example data of command:
        command = "add vacation 2019-12-28:2020-01-03"
        command = "add sick today"
        command = "add vab 2019-12-28 4"
    """

    # validate number of arguments: 3 or 4
    if not len(command) == 3 or len(command) == 4:
        return f"Wrong number of arguments: {len(command)}"

    # store and validate reason
    reason = command[1]
    if not validate_reason(reason=reason, reasons=REASONS):
        return f"arg reason: {reason} is invalid"


    # assign hours a default value of 8
    hours = 8

    # if hours argument was sent: reassing var hours and validate input
    if len(command) == 4:
        hours = command[3]
        if not validate_hours(hours=hours):
            return f"arg hours: {hours} is invalid"

    # store and validate date
    date = command[2]
    
    if not validate_date(date=date):
        return f"arg date: {date} is invalid"

    r = api.create(url=API_URL, event=event)
    if r.status_code != 200:
        return "fail!"


def delete(command: tuple, user_id: str) -> str:
    """Extracts user_id and date from payload and calls api.delete()

    TODO: add support for range
    """

    if not len(command) == 2:
        return f"expected 2 arguments: {len(command)} given"

    date: str = command[1]

    if validate_date(date=date):
        r = api.delete(url=API_URL, date=date, user_id=user_id)
        if r.status_code != 200:
            return f"Could not delete {date}"
    else:
        return f"{date}: not a valid input for date"

    return f"all events for {user_id} on {date} has been deleted"


def ls(command: tuple, user_id: str) -> str:
    return NotImplemented
    """Implements api.read() and Retrieves events for a range or defaults to current month"""


def lock(command: tuple, user_id: str) -> str:
    """Extracts information from payload and calls api.lock()"""

    if not len(command) == 2:
        return f"expected 2 arguments: {len(command)} given"

    # store date
    date: str = command[-1]

    # check if date is valid
    if validate_date(date=date)

        r = api.lock(url=API_URL, user_id=user_id, date=date)

        if r.status_code != 200:
            return f"Could not lock {date}"

    else:
        return f"{date}: not a valid input for date"

    return f"{date} has been locked"


def help_menu() -> str:
    msg = """
        Perform action.

        Supported actions are:
        add - Add new post in timereport
        edit - Not implemented yet
        delete - Delete post in timereport
        list - List posts in timereport
        lock - Not implemented yet
        help - Provide this helpful output
        """
    return msg
