import json
import botocore
import logging
import os
from botocore.exceptions import ClientError
from errorResponse import errorResponse
from utils import assume_role, genpass

logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)

def lambda_handler(event, context):

    accountId = event['pathParameters']['account-id']

    eventBody = json.loads(event["body"])

    username = eventBody["username"]

    try:
        response = createCloudWatchAccount(accountId,username)
    except ClientError as e:
        logger.exception(e)
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def createCloudWatchAccount(AWSAccountId,username):

    session = assume_role(AWSAccountId,os.environ['FUNCTION_POLICY'])

    iam = session.resource('iam')
    
    user = iam.User(username)

    policyArn = "arn:aws:iam::{}:policy/{}".format(AWSAccountId,os.environ['USER_POLICY'])

    try:
        policy = iam.Policy(policyArn).load()
    except ClientError as e:
        logger.exception(e)

        with open('./policies/CloudWatchUserPolicy.json') as f:
            repoPolicy = json.load(f)
            
        iam.create_policy(
            PolicyName=os.environ['USER_POLICY'],
            PolicyDocument=json.dumps(repoPolicy)
        )

    try:
        user.load()
    except ClientError as e:
        logger.exception(e)

        if e.response['Error']['Code'] == 'NoSuchEntity':
             user.create()
    
    password = genpass(8)

    try:
        user.LoginProfile().load()
        
        user.LoginProfile().update(
            Password=password,
            PasswordResetRequired=True
        )
    except ClientError as e:
        logger.exception(e)

        user.LoginProfile().create(
            Password=password,
            PasswordResetRequired=True
        )
   
    user.attach_policy(PolicyArn=policyArn)   

    return {
        'username' : username,
        'password': password
    }

