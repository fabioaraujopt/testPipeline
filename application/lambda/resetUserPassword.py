import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

groupName = 'CloudWatchMonitor'

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    try:
        response = resetUserPasswordCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except botocore.exceptions.ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(errorResponse(e))
        }

    return {
        'statusCode': 200,
        'body':  json.dumps(response)
    }


def resetUserPasswordCloudWatchAccount(AWSAccountId,username):
    
    session = assume_role(str(AWSAccountId))

    iam = session.client('iam')

    #if login exists delete profile
    iam.delete_login_profile(
        UserName=username
    )
    
    password = genpass(8)
    
    #if user do not exists call create user
    #else continue
    login_profile = iam.create_login_profile(
        UserName=username,
        Password=genpass(8),
        PasswordResetRequired=True
    )

    response = {
        'accountId': AWSAccountId,
        'username' : login_profile['LoginProfile']['UserName'],
        'password': password
    }

    return response