import json
import os
from botocore.exceptions import ClientError
from error_response import error_response
from utils import assume_role, genpass, configure_user_client, \
    configure_user_policy, configure_iam_resource, configure_iam_client, logging_config, ENTITY_ALREADY_EXISTS, \
    policy_exists, user_exists

logger = logging_config()



def lambda_handler(event, context):
  
    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _create_cloud_watch_account(account_id, username)
    except ClientError as error:
        logger.exception(error)
        return error_response(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def _create_cloud_watch_account(account_id, username):
    
    login_profile_already_exists = False
    
    session = assume_role(account_id, os.environ['FUNCTION_POLICY'])

    iam = configure_iam_resource(session)
    
    iam_client =  configure_iam_client(session)

    user = configure_user_client(iam, username)

    policy_arn = configure_user_policy(account_id)

    
    if not policy_exists(iam_client, policy_arn):
        with open('./policies/CloudWatchUserPolicy.json') as f:
            repo_policy = json.load(f)

        iam.create_policy(
            PolicyName=os.environ['USER_POLICY'],
            PolicyDocument=json.dumps(repo_policy)
        )
        logger.info("New policy created.")
    
    if not user_exists(iam_client, username): 
        user.create()
        logger.info("New user created.")
    
    password = genpass(8)
    
    #Todo explicit comment
    try:
        user.LoginProfile().create(
                Password=password,
                PasswordResetRequired=True
            )
    except ClientError as error:
        if error.response['Error']['Code'] == ENTITY_ALREADY_EXISTS:
            logger.warning("User already exists.")
            login_profile_already_exists = True
        else:
            raise
    
    if login_profile_already_exists:
        user.LoginProfile().update(
            Password=password,
            PasswordResetRequired=True
        )
    
    user.attach_policy(PolicyArn=policy_arn)
        
    
    return {
        'username': username,
        'password': password
    }


    