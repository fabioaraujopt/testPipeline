import json
import botocore
from errorResponse import errorResponse
from utils import assume_role, genpass

groupName = 'CloudWatchMonitor'

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    try:
        response = createCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except botocore.exceptions.ClientError as e:
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def createCloudWatchAccount(AWSAccountId,username):

    session = assume_role(str(AWSAccountId))

    #verifiy if group and role exists
    #good stuff https://stackoverflow.com/questions/46073435/how-can-we-fetch-iam-users-their-groups-and-policies

    #list users
    #users = client.list_users()

    iam = session.client('iam')

    response = iam.get_group(
        GroupName=groupName
    )

    print(response)

    return True

    
    #if user do not exists (create user)
    iam.create_user(UserName = username)
    
    #if group exists and user not in group
    #if group do not exists create it
    response = iam.add_user_to_group(
        GroupName=groupName,
        UserName=username
    )
    
    password = genpass(8)
    
    #if login profile do not exists create login profile
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