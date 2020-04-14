import json
import string
import random
from utils import assume_role, genpass
import botocore


def lambda_handler(event, context):
    #validate payload
    eventBody = json.loads(event["body"])

    try:
        credentials = createCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except botocore.exceptions.ClientError as e:
        return {
            'statusCode': 400,
            'body': e.response['Error']['Code']
        }

    print (credentials)
    print (json.dumps(credentials))

    return {
        'statusCode': 200,
        'body': credentials
    }
    
def createCloudWatchAccount(AWSAccountId,username):

    print(AWSAccountId, username)
    
    session = assume_role(str(AWSAccountId))

    #catch AccessDenied assume role not allowed
    
    iam = session.client('iam')
    
    iam.create_user(UserName = username)
    
    
    response = iam.add_user_to_group(
        GroupName='CloudWatchMonitor',
        UserName=username
    )
    
    password = genpass(8)
    
    login_profile = iam.create_login_profile(
        UserName=username,
        Password=genpass(8),
        PasswordResetRequired=True
    )

    response = {
        'username' : login_profile['LoginProfile']['UserName'],
        'accountId': AWSAccountId,
        'password': password
    }

    return response
    