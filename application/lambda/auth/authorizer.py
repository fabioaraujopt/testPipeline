import logging
import re
import uuid
import boto3
import auth
import os
import cwexceptions

RESOURCES_GUID = {
    "user" : {
        "DELETE": "b96dffc0-ab86-4679-b989-110742d9d462",
        "PUT": "eb07c9a0-609a-497e-961c-26717c897324"
    },
    "user/password" : { 
        "PATCH": "4bddf46b-e472-45f1-b514-70c8c1005406"
    },
    "policy":{
        "PUT": "0500881c-de42-447d-847c-733504136c9d"
    }
}


logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)

ssm_client = boto3.client('ssm')


def lambda_handler(event, context):
    
    logger.info(event)

    
    resp = ssm_client.get_parameter(
        Name=os.environ['SSM_PUBLIC_KEY_NAME'],
    )
    if resp["Parameter"]["Value"]:
        public_key = resp["Parameter"]["Value"]
    else:
        raise NameError("Public Key was not found within ssm response.")

    logger.info(public_key)
    
    client_token = event['authorizationToken']

    method_arn = event['methodArn']

    tmp = method_arn.split(':')

    api_gateway_arn_tmp = tmp[5].split('/')

    method = api_gateway_arn_tmp[2]

    resource = re.search('(?<=\d\/).*$', method_arn).group(0)

    aws_account_id = tmp[4]

    principal_id = str(uuid.uuid4())

    policy = AuthPolicy(principal_id, aws_account_id)
    policy.rest_api_id = api_gateway_arn_tmp[0]
    policy.region = tmp[3]
    policy.stage = api_gateway_arn_tmp[1]

    #check if guid empty
    guid = RESOURCES_GUID[resource][method]
    
    try:
        auth.validate_token(client_token, public_key, guid)
    except (
        cwexceptions.InvalidBearerPattern,
        cwexceptions.InvalidTokenHeader,
        cwexceptions.InvalidTokenFormat,
        cwexceptions.InvalidTokenSignature,
        cwexceptions.ExpiredToken,
    ):
        logger.error("The token is invalid/expired.")
        # token is not from Auth Server or is invalid/expired (401)
        raise Exception("Unauthorized")
    except cwexceptions.InvalidTokenCapabilities:
        # everything is valid, except for the capabilities (403)
        logger.error("The token is valid, but has incorrect capabilities")
        policy.deny_all_methods()
    else:
        # valid token for the requested method
        policy.allow_method(method, '*')
    
    auth_response = policy.build()
    
    logger.info(auth_response)

    return auth_response