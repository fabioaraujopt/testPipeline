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
        'body': response
    }


def deleteUserCloudWatchAccount(AWSAccountId,username):
    
    session = assume_role(str(AWSAccountId))

    iam = session.client('iam')

    iam.delete_login_profile(
        UserName=username
    )  
    
    iam.remove_user_from_group(
        GroupName=groupName,
        UserName=username
    )

    iam.delete_user(UserName= username)
    
    response = {
        'accountId': AWSAccountId,
        'username' : username
    }

    return response