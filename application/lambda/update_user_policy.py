import json
import os
from botocore.exceptions import ClientError
from error_response import error_response
from utils import assume_role, genpass, configure_user_client, \
    configure_user_policy, configure_iam_resource, configure_iam_client, \
    logging_config, ENTITY_ALREADY_EXISTS, policy_exists, user_exists

logger = logging_config()


def lambda_handler(event, context):

    logger.info(event)

    account_id = event['pathParameters']['account-id']

    event_body = json.loads(event["body"])

    username = event_body["username"]

    try:
        response = _update_user_policy(account_id, username)
    except ClientError as error:
        logger.exception(error)
        return error_response(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def _update_user_policy(account_id, username):

    session = assume_role(account_id, os.environ['FUNCTION_POLICY'])

    iam = configure_iam_resource(session)

    iam_client = configure_iam_client(session)

    user = configure_user_client(iam, username)

    policy_arn = configure_user_policy(account_id)

    if not policy_exists(iam_client, os.environ['USER_POLICY']):
        with open('./policies/CloudWatchUserPolicy.json') as f:
            repo_policy = json.load(f)

        iam.create_policy(
            PolicyName=os.environ['USER_POLICY'],
            PolicyDocument=json.dumps(repo_policy)
        )
        logger.info("New policy created.")

    user.attach_policy(PolicyArn=policy_arn)

    return {
        'username': username
    }
