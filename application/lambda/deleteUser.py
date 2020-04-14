import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

groupName = 'CloudWatchMonitor'

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
    
    session = assume_role(str(AWSAccountId))

    iam = session.client('iam')
    
    #if user exists
    iam.delete_login_profile(
        UserName=username
    )  
    
    #if user is in group
    iam.remove_user_from_group(
        GroupName=groupName,
        UserName=username
    )

    #if user exists
    iam.delete_user(UserName= username)
    
    #if user not in user list
    response = {
        'accountId': AWSAccountId,
        'username' : username
    }

    return response