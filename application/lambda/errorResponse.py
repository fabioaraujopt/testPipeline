
import json

def errorResponse(exception):

    errorCode = exception.response['Error']['Code']

    if(errorCode == "AccessDenied"):
        error_message = "Access denied for account"
    if(errorCode == "EntityAlreadyExists"):
        error_message = "Username already exists"
    else:
        error_message = errorCode

    return {
        "error_message": error_message
    }