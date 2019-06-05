import logging
import json
from chalicelib.lib.list import get_list_data
from chalicelib.lib.slack import (
    slack_responder,
    submit_message_menu,
    slack_client_responder,
    delete_message_menu,
)
from chalicelib.lib.factory import factory
from datetime import datetime

log = logging.getLogger(__name__)


class Action:
    def __init__(self, payload, config):
        self.payload = payload

        try:
            self.params = self.payload["text"][0].split()
        except KeyError:
            log.info("No parameters received. Defaulting to help action")
            self.params = ["help"]

        self.config = config
        self.bot_access_token = config["bot_access_token"]
        self.response_url = self.payload["response_url"][0]

    def perform_action(self):
        """
        Perform action.

        Supported actions are:
        add - Add new post in timereport
        edit - Not implemented yet
        delete - Delete post in timereport
        list - List posts in timereport
        lock - Not implemented yet
        help - Provide this helpful output
        """

        self.action = self.params[0]
        log.debug(f"Action is: {self.action}")
        self.user_id = self.payload["user_id"][0]

        if self.action == "add":
            return self._add_action()

        if self.action == "edit":
            return self._edit_action()

        if self.action == "delete":
            return self._delete_action()

        if self.action == "list":
            return self._list_action()

        if self.action == "lock":
            return self._lock_action()

        if self.action == "help":
            return self._help_action()

        return self._unsupported_action()

    def _unsupported_action(self):
        log.info(f"Action: {self.action} is not supported")
        return self.send_response(message=f"Unsupported action: {self.action}")

    def _add_action(self):
        events = factory(self.payload)
        if not events:
            return self.send_response(message="Wrong arguments for add command")

        log.info(f"Events is: {events}")
        user_name = events[0].get("user_name")[0]
        reason = events[0].get("reason")
        self.date_start = events[0].get("event_date")
        self.date_end = events[-1].get("event_date")
        hours = events[0].get("hours")

        if self.check_lock_state():
            return self.send_response(message="One or more of the events are locked")

        self.attachment = submit_message_menu(
            user_name, reason, self.date_start, self.date_end, hours
        )
        log.info(f"Attachment is: {self.attachment}")
        self.send_response()
        return ""

    def _list_action(self):
        """
        List timereport for user.
        If no arguments supplied it will default to all.

        Supported arguments:
        "today" - List the event for the todays date
        "date" - The date as a string. Use ":" as delimiter for two dates: "2019-01-01:2019-01-02"
        """

        date_str = "all"
        arguments = self.params[1:]

        log.debug(f"Got arguments: {arguments}")
        try:
            if arguments[0] == "today":
                date_str = datetime.now().strftime("%Y-%m-%d")
            else:
                date_str = arguments[0]
        except IndexError as error:
            log.debug(f"got expected exception: {error}", exc_info=True)
            
        list_data = self._get_events(date_str=date_str)

        if not list_data or list_data == '[]':
            log.debug(f"List returned nothing. Date string was: {date_str}")
            self.send_response(message=f"Sorry, nothing to list with supplied argument {arguments}")
            return ""

        self.send_response(message=f"```{list_data}```")
        return ""

    def _delete_action(self):
        date = self.params[1]
        self.attachment = delete_message_menu(self.payload.get("user_name")[0], date)
        log.debug(
            f"Attachment is: {self.attachment}. user_name is {self.payload.get('user_name')[0]}"
        )
        self.send_response()
        return ""

    def _edit_action(self):
        return self.send_response(message="Edit not implemented yet")

    def send_response(self, message=False):
        """
        Send a response to slack

        If param message is False the attribute self.attachment is excpected
        to exist.
        """
        if message:
            slack_responder(url=self.response_url, msg=message)
            return ""

        slack_client_response = slack_client_responder(
            token=self.bot_access_token,
            user_id=self.user_id,
            attachment=self.attachment,
        )
        if slack_client_response.status_code != 200:
            log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            log.debug(f"Slack client response was: {slack_client_response.text}")
        return slack_client_response

    def _help_action(self):
        return self.send_response(message=f"{self.perform_action.__doc__}")

    def check_lock_state(self):
        """
        Go through events and check if locked

        Return true if any locked events found
        """

        for event in json.loads(self._get_events(date_str=f"{self.date_start}:{self.date_end}")):
            if event.get("lock"):
                return True
        
        return False

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}",
            self.user_id,
            date_str=date_str,
        )
    
    def _lock_action(self):
        return self.send_response(message="Lock not implemented yet")