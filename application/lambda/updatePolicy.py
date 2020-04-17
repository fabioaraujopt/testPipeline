import json
import botocore
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass


userPolicyName = "testPolicy" #.env
lambdaRoleName = "CWUsers" #.env

def lambda_handler(event, context):

    eventBody = json.loads(event["body"])

    accountId = eventBody["accountId"]

    try:
        response = updateCloudWatchPolicy(accountId)
    except ClientError as e:
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def updateCloudWatchPolicy(AWSAccountId):

    session = assume_role(AWSAccountId,lambdaRoleName)

    iam = session.resource('iam')
    
    policyArn = "arn:aws:iam::{}:policy/{}".format(AWSAccountId,userPolicyName)

    with open('./policies/CWUser.json') as f:
            repoPolicy = json.load(f)

    try:
        policy = iam.Policy(policyArn).load()
        policy.create_version(
            PolicyDocument=repoPolicy,
            SetAsDefault=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':  
            iam.create_policy(
                PolicyName=userPolicyName,
                PolicyDocument=json.dumps(repoPolicy)
            )

    return {
        'accountId': AWSAccountId,
        'policy_arn': policyArn
    }

