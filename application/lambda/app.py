import json
import string
import random


def lambda_handler(event, context):

    eventBody = event["body"]

    try:
        createdAccount = createCloudWatchAccount(eventBody["accountId"],eventBody["username"])
    except Exception as e: 
        print(e)
        
    return {
        'statusCode': 200,
        'body': createdAccount
    }
    
def createCloudWatchAccount(AWSAccountId,username):
    
    session = assume_role(str(AWSAccountId))
    
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
    
    login_profile['LoginProfile']['password'] = genpass(8) 
    
    return login_profile
    