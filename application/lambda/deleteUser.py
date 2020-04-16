import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    try:
        response = deleteUserCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except botocore.exceptions.ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(errorResponse(e))
        }

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
    except:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            pass

    try:
        user.LoginProfile().load()
    except:
        user.LoginProfile().delete()
    
    user.delete()

    return {
        'accountId': AWSAccountId,
        'username' : username,
        }
    
    



