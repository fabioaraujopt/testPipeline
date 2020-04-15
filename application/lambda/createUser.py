import json
import botocore
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass, isUsernameInGroup

groupName = 'CloudWatchMonitor'

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    #try:
    response = createCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    #except botocore.exceptions.ClientError as e:
    #    return errorResponse(e)

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

    try:
        iamGroup = iam.Group("adfdfadsf")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            groupUsers = iam.create_group(
                GroupName="adfdfadsf"
            )
            #group_policy = group.create_policy(
            #    PolicyName='string',
            #    PolicyDocument='string'
            #)
           
    iamGroup = iam.get_group(
            GroupName=groupName
        )
    
    
    print('not existent group', groupUsers)

    username = "joao"

    print ('is username in group', username, isUsernameInGroup(iamGroup,username))

    username = "fasdfasdfasdfa"

    print ('is username in group', username, isUsernameInGroup(iamGroup,username))



    return True

    #simular não existir grupo 
    #não existir 

    #check if user exists
    iam.create_user(UserName = username)

    if not isUsernameInGroup(iamGroup,username):
        iam.add_user_to_group(GroupName=groupName,UserName=username)

   
    
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

