import json
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assumeRole, genPass, configureUserClient, \
    configureUserPolicy, configureIamClient, loggingConfig, NO_SUCH_ENTITY


logger = loggingConfig()

def lambda_handler(event, context):

    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _create_cloud_watch_account(account_id, username)
    except ClientError as error:
        logger.exception(error)
        return errorResponse(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def _create_cloud_watch_account(account_id, username):
    
    session = assumeRole(account_id, os.environ['FUNCTION_POLICY'])

    iam = configureIamClient(session)

    user = configureUserClient(iam, username)

    policy_arn = configureUserPolicy(account_id)

    try:
        iam.Policy(policy_arn).load()
    except ClientError as error:
        logger.exception(error)

        with open('./policies/CloudWatchUserPolicy.json') as f:
            repo_policy = json.load(f)
            
        iam.create_policy(
            PolicyName=os.environ['USER_POLICY'],
            PolicyDocument=json.dumps(repo_policy)
        )

    try:
        user.load()
    except ClientError as error:
        logger.exception(error)

        if error.response['Error']['Code'] == NO_SUCH_ENTITY:
             user.create()
    
    password = genPass(8)

    try:
        user.LoginProfile().load()
        user.LoginProfile().update(
            Password=password,
            PasswordResetRequired=True
        )
    except ClientError as error:
        logger.exception(error)
        user.LoginProfile().create(
            Password=password,
            PasswordResetRequired=True
        )

    user.attach_policy(PolicyArn=policy_arn)     

    return {
        'username' : username,
        'password': password
    }

