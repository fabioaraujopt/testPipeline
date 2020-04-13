import json
import boto3
import botocore
import secrets
import string
import random


def lambda_handler(event, context):

#except EntityAlreadyExistsException
    
    return {
        'event': json.dumps(event), 
        'context': json.dumps(context)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def assume_role(account_id):
    sts = boto3.client("sts")
    
    role_arn = "arn:aws:iam::{}:role/CloudWatchManagement2".format(account_id)
    try:
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="CloudWatchService")
        print (resp)
    except botocore.exceptions.ClientError as e:
        raise e

    if "Credentials" not in resp:
        raise Exception("Unable to assume role %s on %s.",
                        'CloudWatchService',
                        account_id)

    creds = resp["Credentials"]
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"])
    return session



def genpass(length):
    """Generate a random password.
    Args:
        length(int): Password length
    Returns:
        str: random password
    """
    password = ""
    choice = string.ascii_letters + string.digits
    for i in range(length):
        password += random.choice(choice)
    return password
    
    
    
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
    
def updateCloudWatchAccount():
    print("todd")