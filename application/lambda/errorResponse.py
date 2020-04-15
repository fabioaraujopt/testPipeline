
import json

def errorResponse(exception):

    errorCode = exception.response['Error']['Code']
    
    if(errorCode == "AccessDenied"):
        error_message = "Access denied for account"
        statusCode = 403
    elif(errorCode == "EntityAlreadyExists"):
        error_message = "Username already exists"
        statusCode = 400
    elif(errorCode == "NoSuchEntity"):
        error_message = "Username do not exists"
        statusCode = 404
    elif(errorCode == "EntityTemporarilyUnmodifiable"):
        error_message = "User cannot be modified"
        statusCode = 409
    else:
        error_message = errorCode
        statusCode = 400

    return {
            'statusCode': statusCode,
            'body': json.dumps({
                    "message": error_message
                })
        }