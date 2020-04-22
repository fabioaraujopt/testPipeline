import json
import botocore
import logging
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass

logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)


def lambda_handler(event, context):

    logger.info(event)

    accountId = event['pathParameters']['account-id']

    eventBody = json.loads(event["body"])

    username = eventBody["username"]

    try:
        response = resetUserPasswordCloudWatchAccount(accountId,username)
    except ClientError as e:
        logger.exception(e)
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body':  json.dumps(response)
    }


def resetUserPasswordCloudWatchAccount(AWSAccountId,username):
    
    session = assume_role(AWSAccountId,os.environ['FUNCTION_POLICY'])

    iam = session.resource('iam')

    user = iam.User(username)

    user.load()
    
    password = genpass(8)

    user.LoginProfile().load()

    user.LoginProfile().update(
        Password=password,
        PasswordResetRequired=True
    )
    
    return {
        'username' : username,
        'password': password
    }