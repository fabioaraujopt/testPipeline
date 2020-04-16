import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    try:
        response = resetUserPasswordCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except botocore.exceptions.ClientError as e:
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

    try:
        user.LoginProfile().load()
        user.LoginProfile().update(
            Password=password,
            PasswordResetRequired=True
        )
    except:
        user.LoginProfile().create(
            Password=password,
            PasswordResetRequired=True
        )
    
    return {
        'accountId': AWSAccountId,
        'username' : username,
        'password': password
    }