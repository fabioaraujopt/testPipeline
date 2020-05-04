import boto3
import botocore
import string
import random
import os
import logging

NO_SUCH_ENTITY = "NoSuchEntity"
ENTITY_ALREADY_EXISTS = "EntityAlreadyExists"


def logging_config():
    logger = logging.getLogger(name=__name__)
    log_level = logging.INFO
    logger.setLevel(log_level)

    return logger

def configure_iam_client(session):
    return session.client('iam')


def policy_exists(iam_client, policy_name):

    response = iam_client.list_policies(
        Scope='All',
        OnlyAttached=False
    )

    for policy in response["Policies"]:
        if policy["PolicyName"] == policy_name:
            return True
    return False

def user_exists(iam_client, username):
    response = iam_client.list_users()

    for user in response["Users"]:
        if user["UserName"] == username:
            return True
    return False


def policy_attached_to_user(iam_client, username, policy_name):
    response = iam_client.list_attached_user_policies(
        UserName=username
    )

    for policy in response["AttachedPolicies"]:
        if policy["PolicyName"] == policy_name:
            return True
    return False



def configure_iam_resource(session):
    return session.resource('iam')


def configure_user_client(iam, username):
    return iam.User(username)


def configure_user_policy(account_id):
    return "arn:aws:iam::{}:policy/{}".format(account_id, os.environ['USER_POLICY'])


def assume_role(account_id, role_to_assume):
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
