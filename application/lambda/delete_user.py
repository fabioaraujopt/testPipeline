import json
import botocore
import os
from botocore.exceptions import ClientError
from error_response import error_response
from utils import assume_role, genpass, configure_user_client, \
    configure_user_policy, configure_iam_resource, configure_iam_client, logging_config, NO_SUCH_ENTITY, \
    policy_attached_to_user, user_exists

logger = logging_config()


def lambda_handler(event, context):
    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _delete_user_cloudwatch_account(account_id, username)
    except ClientError as error:
        return error_response(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def _delete_user_cloudwatch_account(account_id, username):
    session = assume_role(account_id, os.environ['FUNCTION_POLICY'])

    iam = configure_iam_resource(session)

    iam_client =  configure_iam_client(session)

    user = configure_user_client(iam, username)

    policy_arn = configure_user_policy(account_id)

    if not user_exists(iam_client, username):
        return {'username': username}

    if policy_attached_to_user(iam_client, username, os.environ['USER_POLICY']):
        user.detach_policy(PolicyArn=policy_arn)
        logger.info("Policy detached.")

    #if login profile was already deleted continue code execution 
    #at current version there is no api to get list of login profiles
    try:
        user.LoginProfile().delete()
    except ClientError as error:
        if error.response['Error']['Code'] == NO_SUCH_ENTITY:
            logger.warning("Login profile does not exist.")
        else:
            logger.error(error)
            raise

    user.delete()

    return {'username': username}
