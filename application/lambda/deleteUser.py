import json
import botocore
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assumeRole, configureUserClient, configureUserPolicy,\
    configureUserPolicy, configureIamClient, loggingConfig, NO_SUCH_ENTITY


logger = loggingConfig()

def lambda_handler(event, context):

    logger.info(event)

    account_id = event['pathParameters']['account-id']
    
    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _delete_user_cloudwatch_account(account_id, username)
    except ClientError as error:
        return errorResponse(error)

    return {
        'statusCode': 200,
        'body':  json.dumps(response)
    }


def _delete_user_cloudwatch_account(account_id, username):

    session = assumeRole(account_id, os.environ['FUNCTION_POLICY'])

    iam = configureIamClient(session)

    user = configureUserClient(iam, username)

    policy_arn = configureUserPolicy(account_id)

    try:
        user.load()
    except ClientError as error:
        logger.exception(error)

        if error.response['Error']['Code'] == NO_SUCH_ENTITY:
            return {
                'username' : username
            }
    
    try:
        user.detach_policy(PolicyArn=policy_arn)
    except ClientError as error:
        logger.exception(error)

        if error.response['Error']['Code'] == 'NoSuchEntity':
            pass

    try:
        user.LoginProfile().load()
        user.LoginProfile().delete()
    except:
        pass
    
    user.delete()

    return {'username' : username}
    
    



