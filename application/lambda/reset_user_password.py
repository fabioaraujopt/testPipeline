import json
import botocore
import logging
import os
from botocore.exceptions import ClientError
from error_response import error_response
from utils import assume_role, genpass, configure_user_client, \
    configure_user_policy, configure_iam_client, logging_config

logger = logging_config()


def lambda_handler(event, context):
    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _reset_user_password_cloudwatch_account(account_id, username)
    except ClientError as error:
        logger.exception(error)
        return error_response(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def _reset_user_password_cloudwatch_account(account_id, username):
    session = assume_role(account_id, os.environ['FUNCTION_POLICY'])

    iam = configure_iam_client(session)

    user = configure_user_client(iam, username)

    user.load()

    password = genpass(8)

    user.LoginProfile().load()

    user.LoginProfile().update(
        Password=password,
        PasswordResetRequired=True
    )

    return {
        'username': username,
        'password': password
    }
