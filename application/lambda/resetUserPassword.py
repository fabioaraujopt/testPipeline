import json
import botocore
import logging
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assumeRole, genPass, \
    configureUserPolicy, configureIamClient, loggingConfig, configureUserClient


logger = loggingConfig()

def lambda_handler(event, context):

    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _reset_user_password_cloudwatch_account(account_id, username)
    except ClientError as error:
        logger.exception(error)
        return errorResponse(error)

    return {
        'statusCode': 200,
        'body':  json.dumps(response)
    }


def _reset_user_password_cloudwatch_account(account_id, username):
    
    session = assumeRole(account_id, os.environ['FUNCTION_POLICY'])

    iam = configureIamClient(session)

    user = configureUserClient(iam,username)

    user.load()
    
    password = genPass(8)

    user.LoginProfile().load()

    user.LoginProfile().update(
        Password=password,
        PasswordResetRequired=True
    )
    
    return {
        'username' : username,
        'password': password
    }