import boto3
import botocore
import string
import random
import os
import logging

NO_SUCH_ENTITY = "NoSuchEntity"


def loggingConfig():
    logger = logging.getLogger(name=__name__)
    log_level = logging.INFO
    logger.setLevel(log_level)
    
    return logger

def configureIamClient(session):
    return session.resource('iam')

def configureUserClient(iam, username):
    return iam.User(username)

def configureUserPolicy(account_id):
    return "arn:aws:iam::{}:policy/{}".format(account_id, os.environ['USER_POLICY'])

def assumeRole(account_id, role_to_assume):
    
    sts = boto3.client("sts")
    
    role_arn = "arn:aws:iam::{}:role/{}".format(account_id, role_to_assume)

    try:
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="CloudWatchService")
        
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

def genPass(length):
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
