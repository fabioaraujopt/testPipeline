import json
import os
from botocore.exceptions import ClientError
from error_response import error_response
from utils import assume_role, configure_user_policy, configure_iam_client, \
    logging_config, policy_exists

logger = logging_config()


def lambda_handler(event, context):
    logger.info(event)

    account_id = event['pathParameters']['account-id']

    try:
        response = _update_account_policy(account_id)
    except ClientError as error:
        logger.exception(error)

        return error_response(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def _update_account_policy(account_id):
    session = assume_role(account_id, os.environ['FUNCTION_POLICY'])

    iam = configure_iam_client(session)

    iam_client = configure_iam_client(session)

    policy_arn = configure_user_policy(account_id)

    with open('./policies/CloudWatchUserPolicy.json') as f:
        repo_policy = json.load(f)

    if not policy_exists(iam_client, os.environ['USER_POLICY']):
        iam.create_policy(
            PolicyName=os.environ['USER_POLICY'],
            PolicyDocument=json.dumps(repo_policy)
        )
        logger.info("New policy created.")

    policy = iam.get_policy(PolicyArn=policy_arn)

    policy_default_version = iam.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy["Policy"]["DefaultVersionId"]
    )

    policy_document = policy_default_version["PolicyVersion"]["Document"]

    if policy_document != repo_policy:
        iam.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=json.dumps(repo_policy),
            SetAsDefault=True
        )

    return {
        'policy_arn': policy_arn
    }
