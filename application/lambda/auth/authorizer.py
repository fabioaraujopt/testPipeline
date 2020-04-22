import logging
import re
import uuid
import boto3
import auth

API_OPERATIONS = {
    "CreateCloudWatchUser" : "eb07c9a0-609a-497e-961c-26717c897324",
    "DeleteCloudWatchUser" : "b96dffc0-ab86-4679-b989-110742d9d462",
    "ResetPasswordCloudWatchUser" : "4bddf46b-e472-45f1-b514-70c8c1005406",
    "UpdatePolicyCloudWatch" : "0500881c-de42-447d-847c-733504136c9d"
}

publicKey = "PFJTQUtleVZhbHVlPjxNb2R1bHVzPmhVRWxmNytBRE1nUHEvcmV0NDArZ1lQaVZWZjhDQzdjc0NVZzRMMGpaeC9xeFU3WEJHN1plUEpWZ3c2TzJZdXFFcFFocTh5a0Q4Y0tmbVExNnVmaDVDcDk0VmhReFl6bGdTY2p3aUdkbFUvUzh0WDROY1ZmOGZJb1hHRDdkV0tQalV6V3RtUC9MM0h3alpXU1J4L3hDUzRsWjFvZThRRnEzQjZxMVJ0czdneTZIaDhKZXlNYXlrNVp1RlpZcVBGWmIxU21PZkJXRFkvZWkxK1duUVFrb1MyYjNwVGhxakdUTk5oWGFMdGZtV05xK1dnMEpZWVdkVTd6NE94dUlCbjJvL3NWQUVRT0piSEZzb2FUckFoajI1NmhBb0J6WjlKWlJUSmhIelcweEJXYWRLVEVMcDd3R3dPK0xiMWR1KzJXOGpxdWJVSWZyUFByWkJncnFST0tZUT09PC9Nb2R1bHVzPjxFeHBvbmVudD5BUUFCPC9FeHBvbmVudD48L1JTQUtleVZhbHVlPg=="


logger = logging.getLogger(name=__name__)
log_level = logging.INFO
logger.setLevel(log_level)

ssm_client = boto3.client('ssm')


def lambda_handler(event, context):
    
    logger.info(event)
    
    client_token = event['authorizationToken']

    method_arn = event['methodArn']

    tmp = method_arn.split(':')

    api_gateway_arn_tmp = tmp[5].split('/')

    method = api_gateway_arn_tmp[2]

    resource = re.search('\d\/.+$', method_arn)

    aws_account_id = tmp[4]

    principal_id = str(uuid.uuid4())

    policy = AuthPolicy(principal_id, aws_account_id)
    policy.rest_api_id = api_gateway_arn_tmp[0]
    policy.region = tmp[3]
    policy.stage = api_gateway_arn_tmp[1]

    print(resource)

    return True


    if method == HttpVerb.PUT:
        required_capabilites = API_OPERATION_POST_CAPABILITIES[resource]
        child_resource = ''
    elif method == HttpVerb.POST:
        required_capabilites = API_OPERATION_GET_CAPABILITIES[resource]
        child_resource = ''.join(["/", api_gateway_arn_tmp[4]])
    else:
        raise NameError(f"Invalid method name: {method}")







    return {
      "principalId": "user",
      "policyDocument": {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Action": "execute-api:Invoke",
            "Effect": "Allow",
            "Resource": "arn:aws:execute-api:us-east-1:*:*/*/*/*"
          }
        ]
      }
    }

    '''
    Typically the event has 3 keys:
    {
        "type":"TOKEN",
        "authorizationToken":"<caller-supplied-token>",
        "methodArn":"arn:aws:execute-api:<regionId>:<accountId>:<apiId>/<stage>/<method>/<resourcePath>"
    }

    Note: There is a limitation in Lambda Authorizers, where in the case of
    invalid token (format or permissions), the response can only be http
    error 401 "Unauthorized" by raising Exception("Unauthorized") or http
    error 403 "Forbidden" by explicitly denying access to all API methods
    '''

    # the public key must be available as a parameter
    """
    resp = ssm_client.get_parameter(
        Name="auth-server-pub-key",
    )
    
    if resp["Parameter"]["Value"]:
        public_key = resp["Parameter"]["Value"]
    else:
        raise NameError("Public Key was not found within ssm response.")
    """

    tmp = method_arn.split(':')
    api_gateway_arn_tmp = tmp[5].split('/')

    aws_account_id = tmp[4]
    principal_id = str(uuid.uuid4())

    policy = AuthPolicy(principal_id, aws_account_id)
    policy.rest_api_id = api_gateway_arn_tmp[0]
    policy.region = tmp[3]
    policy.stage = api_gateway_arn_tmp[1]

    method = api_gateway_arn_tmp[2]
    resource = api_gateway_arn_tmp[3]

    if method == HttpVerb.POST:
        required_capabilites = API_OPERATION_POST_CAPABILITIES[resource]
        child_resource = ''
    elif method == HttpVerb.GET:
        required_capabilites = API_OPERATION_GET_CAPABILITIES[resource]
        child_resource = ''.join(["/", api_gateway_arn_tmp[4]])
    else:
        raise NameError(f"Invalid method name: {method}")

    # The API GW will parse Exception message to the corresponding HTTP error
    try:
        auth.validate_token(client_token, public_key, required_capabilites)
    except (
        vpnexceptions.InvalidBearerPattern,
        vpnexceptions.InvalidTokenHeader,
        vpnexceptions.InvalidTokenFormat,
        vpnexceptions.InvalidTokenSignature,
        vpnexceptions.ExpiredToken,
    ):
        log.exception("The token is invalid/expired.")
        # token is not from Auth Server or is invalid/expired (401)
        raise Exception("Unauthorized")
    except vpnexceptions.InvalidTokenCapabilities:
        # everything is valid, except for the capabilities (403)
        log.exception("The token is valid, but has incorrect capabilities")
        policy.deny_all_methods()
    else:
        # valid token for the requested method
        policy.allow_method(method, resource + child_resource)

    # Finally, build the policy
    auth_response = policy.build()

    return auth_response


class HttpVerb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


class AuthPolicy:
    aws_account_id = ''
    principal_id = ''
    version = '2012-10-17'
    path_regex = r'^[/.a-zA-Z0-9-*]+$'

    '''Internal lists of allowed and denied methods.

    These are lists of objects and each object has 1 property: A resource
    ARN. The build method processes these lists and generates the approriate
    statements for the final policy.
    '''
    allow_methods = []
    deny_methods = []
    rest_api_id = '*'
    region = '*'
    stage = '*'

    def __init__(self, principal, aws_account_id):
        self.aws_account_id = aws_account_id
        self.principal_id = principal
        self.allow_methods = []
        self.deny_methods = []

    def _add_method(self, effect, verb, resource):
        '''
        Adds a method to the internal lists of allowed or denied methods.
        Each object in the internal list contains a resource ARN and a
        condition statement. The condition statement can be null.
        '''

        if verb != '*' and not hasattr(HttpVerb, verb):
            raise NameError(
                f"Invalid HTTP verb {verb}.",
            )
        resource_pattern = re.compile(self.path_regex)
        if not resource_pattern.match(resource):
            raise NameError(
                f"Invalid resource path: {resource}."
                f" Path should match {self.path_regex}",
            )

        if resource[:1] == '/':
            resource = resource[1:]

        resource_arn = (
            f"arn:aws:execute-api:{self.region}:{self.aws_account_id}:"
            f"{self.rest_api_id}/{self.stage}/{verb}/{resource}"
        )

        if effect.lower() == 'allow':
            self.allow_methods.append(
                {
                    'resourceArn': resource_arn,
                },
            )
        elif effect.lower() == 'deny':
            self.deny_methods.append(
                {
                    'resourceArn': resource_arn,
                },
            )

    def _get_empty_statement(self, effect):
        '''
        Returns an empty statement object prepopulated with the correct
        action and the desired effect.
        '''
        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': [],
        }
        return statement

    def _get_statement_for_effect(self, effect, methods):
        '''This function loops over an array of objects containing a
         resourceArn and conditions statement and generates the array of
          statements for the policy.'''
        statements = []

        if methods:
            statement = self._get_empty_statement(effect)

            for cur_method in methods:
                statement['Resource'].append(cur_method['resourceArn'])

            if statement['Resource']:
                statements.append(statement)
        return statements

    def deny_all_methods(self):
        '''Adds a '*' allow to the policy to deny access to all methods of
            an API'''
        self._add_method('Deny', HttpVerb.ALL, '*')

    def allow_method(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list
        of allowed methods for the policy'''
        self._add_method('Allow', verb, resource)

    def build(self):
        '''
        Generates the policy document based on the internal lists of
        allowed and denied conditions. This will generate a policy with
        two main statements for the effect: one statement for Allow and
         one statement for Deny.
         '''
        if ((self.allow_methods is None or not self.allow_methods) and
                (self.deny_methods is None or not self.deny_methods)):
            raise NameError("No statements defined for the policy")

        policy = {
            'principalId': self.principal_id,
            'policyDocument': {
                'Version': self.version,
                'Statement': [],
            },
        }
        policy['policyDocument']['Statement'].extend(
            self._get_statement_for_effect('Allow', self.allow_methods),
        )
        policy['policyDocument']['Statement'].extend(
            self._get_statement_for_effect('Deny', self.deny_methods),
        )

        return policy