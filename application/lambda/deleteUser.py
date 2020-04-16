import json
import botocore
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass


userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    accountId = eventBody["accountId"]
    username = eventBody["username"]

    #try:
    response = deleteUserCloudWatchAccount(accountId,username)
    #except ClientError as e:
    #return errorResponse(e)

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
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return {
                'accountId': AWSAccountId,
                'username' : username,
            }
    
    try:
        user.detach_policy(PolicyArn=policyArn)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            pass

    try:
        user.LoginProfile().load()
        user.LoginProfile().delete()
    except:
        pass
    
    user.delete()

    return {
        'accountId': AWSAccountId,
        'username' : username,
        }
    
    



