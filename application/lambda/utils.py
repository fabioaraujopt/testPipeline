import boto3
import botocore
import secrets
import string
import random


def assume_role(account_id):
    sts = boto3.client("sts")
    
    role_arn = "arn:aws:iam::{}:role/CWUsers".format(account_id)

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

def isUsernameInGroup(iamGroup, username):
    for user in iamGroup["Users"]:
        if user["UserName"] == username:
            return True
    return False

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
    
#TODO error parser
    #user not found 400
    #not role sts 400