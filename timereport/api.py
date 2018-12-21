import json
import logging

from timereport.lib.factory import factory
from timereport.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons
from timereport.lib.add import post_to_backend

logger = logging.getLogger()

with open('config.json') as fd:
    config = json.load(fd)
    valid_reasons = config['valid_reasons']
    valid_actions = config['valid_actions']
    backend_url = config['backend_url']
    logger.setLevel(config['log_level'])

def lambda_handler(event, context):

    payload = slack_payload_extractor(event)
    events = factory(payload)
    action = payload['text'].split('+')[0]
    command = payload['text'].split('+')[1:]
    auth_token = payload['team_id']

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    verify_reasons(valid_reasons, command[0])
    verify_actions(valid_actions, action)

    if action == "add":
        for e in events:
            post_to_backend(backend_url, e, auth_token)
