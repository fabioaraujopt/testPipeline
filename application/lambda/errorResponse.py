
import json

def errorResponse(exception):

    errorCode = exception.response['Error']['Code']
    error_message = exception.response['Error']['Message']

    if(errorCode == "AccessDenied"):
        error_message = "Access denied for account"
    if(errorCode == "EntityAlreadyExists"):
        error_message = "Username already exists"
    if(errorCode == "NoSuchEntity"):
        error_message = "Username do not exists"
        
    else:
        error_message = errorCode

    return {
        "error_code": errorCode,
        "error_message": error_message
    }