import json
import botocore
import logging
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass

logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)

userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    accountId = eventBody['pathParameters']['account-id']
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
    
    session = assume_role(AWSAccountId,lambdaRoleName)

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
        'accountId': AWSAccountId,
        'username' : username,
        'password': password
    }