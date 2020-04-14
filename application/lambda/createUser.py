import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

groupName = 'CloudWatchMonitor'

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    #try:
    response = createCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    #except botocore.exceptions.ClientError as e:
    #    return {
    #        'statusCode': 400,
    #        'body': json.dumps(errorResponse(e))
    #    }

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def createCloudWatchAccount(AWSAccountId,username):

    session = assume_role(str(AWSAccountId))

    iam = session.client('iam')
    
    #if exists reset
    iam.create_user(UserName = username)
    
    response = iam.add_user_to_group(
        GroupName=groupName,
        UserName=username
    )
    
    password = genpass(8)
    
    #if login pri
    login_profile = iam.create_login_profile(
        UserName=username,
        Password=genpass(8),
        PasswordResetRequired=True
    )
    #todo if do not exist update

    response = {
        'accountId': AWSAccountId,
        'username' : login_profile['LoginProfile']['UserName'],
        'password': password
    }

    return response