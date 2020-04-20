import json
import botocore
import logging
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass

logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)

userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    accountId = event['pathParameters']['account-id']

    try:
        response = updateCloudWatchPolicy(accountId)
    except ClientError as e:
        logger.exception(e)

        return errorResponse(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def updateCloudWatchPolicy(AWSAccountId):
    
    session = assume_role(AWSAccountId,lambdaRoleName)

    iam = session.client('iam')
    
    policyArn = "arn:aws:iam::{}:policy/{}".format(AWSAccountId,userPolicyName)

    with open('./policies/CWUser.json') as f:
            repoPolicy = json.load(f)
    
    try:
        policy = iam.get_policy(
            PolicyArn=policyArn
        )
    except ClientError as e:
        logger.exception(e)

        if e.response['Error']['Code'] == 'NoSuchEntity':  
            policy = iam.create_policy(
                PolicyName=userPolicyName,
                PolicyDocument=json.dumps(repoPolicy),
            )
        
    policyDefaultVersion = iam.get_policy_version(
        PolicyArn=policyArn,
        VersionId=policy["Policy"]["DefaultVersionId"]
    )
    
    policyDocument = policyDefaultVersion["PolicyVersion"]["Document"]
    
    if(policyDocument != repoPolicy):
        response = iam.create_policy_version(
            PolicyArn=policyArn,
            PolicyDocument=json.dumps(repoPolicy),
            SetAsDefault=True
        )
    
    return {
        'policy_arn': policyArn
    }
    
