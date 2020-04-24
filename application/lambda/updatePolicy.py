import json
import botocore
import logging
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assumeRole, genPass, configureUserClient,\
    configureUserPolicy, configureIamClient, loggingConfig, NO_SUCH_ENTITY

logger = loggingConfig()

def lambda_handler(event, context):

    logger.info(event)

    account_id = event['pathParameters']['account-id']

    try:
        response = _update_cloudwatch_policy(account_id)
    except ClientError as error:
        logger.exception(error)

        return errorResponse(error)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def _update_cloudwatch_policy(account_id):
    
    session = assumeRole(account_id, os.environ['FUNCTION_POLICY'])

    iam = configureIamClient(session)

    policy_arn = configureUserPolicy(account_id)

    with open('./policies/CloudWatchUserPolicy.json') as f:
            repo_policy = json.load(f)
    
    try:
        policy = iam.get_policy(
            PolicyArn=policy_arn
        )
    except ClientError as error:
        logger.exception(error)

        if error.response['Error']['Code'] == NO_SUCH_ENTITY:  
            policy = iam.create_policy(
                PolicyName=os.environ['USER_POLICY'],
                PolicyDocument=json.dumps(repo_policy),
            )
        
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
    
