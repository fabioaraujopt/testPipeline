
import json

def errorResponse(exception):

    errorCode = exception.response['Error']['Code']
    
    if(errorCode == "AccessDenied"):
        error_message = "Access denied for account"
    if(errorCode == "EntityAlreadyExists"):
        error_message = "Username already exists"
    if(errorCode == "NoSuchEntity"):
        error_message = "Username do not exists"
    if(errorCode == "EntityTemporarilyUnmodifiable"):
        error_message = "User cannot be modified"
    else:
        error_message = errorCode

    return {
        "error_message": error_message
    }