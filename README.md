# CloudWatchUsers API
This feature was implemented to manage cloudwatch users in accounts.

## Deployment
To deploy this feature the following steps must be followed:

The lambdas implemented by this feature have an authentication layer as dependency. Please ensure layer is deployed or follow the deployment steps in the repository [apigw_lambda_authorizer_auth-layer](https://github.com/OutSystems/apigw_lambda_authorizer_auth-layer).
1. Open cloudformation and upload pipeline.yaml
2. Fill the required parameters
   - OSAuth server public key must be in **base64*
   - AuthLayerArn can be retreived in the layer Cloudformation output variables.
   - Edit AuthServerPubKeyName placeholder with project name
3. Wait till pipeline finishes execution
4. Go to apigateway and look for name `{project-name}-apigateway`, go to stages and retreive base url to be used.

### Roles
This feature produces changes in foreign accounts so a role must be set up in each foreing account in order to allow the lambdas to work
1. Create a role in foreign account called `CloudWatchUserFunctionRole` the policy to be included is present in this repository in `/application/lambda/policies/CloudWatchUserFunctionRole.json`
2. Inside the role go to Trust Relationships, then click in edit relationships and add the policy present in this repository in `/application/lambda/policies/CloudWatchUserFunctionRoleTrustRelatioship.json.json`, replace the placeholder with the account-id where this feature is being implemented to (not the role one).

