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

    accountId = event['pathParameters']['account-id']
    
    eventBody = json.loads(event["body"])

    username = eventBody["username"]

    try:
        response = deleteUserCloudWatchAccount(accountId,username)
    except ClientError as e:
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body':  json.dumps(response)
    }


def deleteUserCloudWatchAccount(AWSAccountId,username):
    
    session = assume_role(AWSAccountId,lambdaRoleName)

    iam = session.resource('iam')

    user = iam.User(username)

    policyArn = "arn:aws:iam::{}:policy/{}".format(AWSAccountId,userPolicyName)

    try:
        user.load()
    except ClientError as e:
        logger.exception(e)

        if e.response['Error']['Code'] == 'NoSuchEntity':
            return {
                'accountId': AWSAccountId,
                'username' : username,
            }
    
    try:
        user.detach_policy(PolicyArn=policyArn)
    except ClientError as e:
        logger.exception(e)

        if e.response['Error']['Code'] == 'NoSuchEntity':
            pass

    try:
        user.LoginProfile().load()
        
        user.LoginProfile().delete()
    except:
        pass
    
    user.delete()

    return {
        'username' : username,
        }
    
    



