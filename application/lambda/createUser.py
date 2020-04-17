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

    username = eventBody["username"]

    try:
        response = createCloudWatchAccount(accountId,username)
    except ClientError as e:
        return errorResponse(e)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def createCloudWatchAccount(AWSAccountId,username):

    session = assume_role(AWSAccountId,lambdaRoleName)

    iam = session.resource('iam')
    
    user = iam.User(username)

    policyArn = "arn:aws:iam::{}:policy/{}".format(AWSAccountId,userPolicyName)

    try:
        policy = iam.Policy(policyArn).load()
    except:
        with open('./policies/CWUser.json') as f:
            repoPolicy = json.load(f)
            
        iam.create_policy(
            PolicyName=userPolicyName,
            PolicyDocument=json.dumps(repoPolicy)
        )

    try:
        user.load()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
             user.create()
    
    password = genpass(8)

    try:
        user.LoginProfile().load()
        
        user.LoginProfile().update(
            Password=password,
            PasswordResetRequired=True
        )
    except:
        user.LoginProfile().create(
            Password=password,
            PasswordResetRequired=True
        )
   
    user.attach_policy(PolicyArn=policyArn)   

    return {
        'accountId': AWSAccountId,
        'username' : username,
        'password': password
    }

