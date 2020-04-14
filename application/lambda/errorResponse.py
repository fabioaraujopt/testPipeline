
import json

def errorResponse(exception):

    errorCode = exception.response['Error']['Code']
    
    if(errorCode == "AccessDenied"):
        error_message = "Access denied for account"
    elif(errorCode == "EntityAlreadyExists"):
        error_message = "Username already exists"
    elif(errorCode == "NoSuchEntity"):
        error_message = "Username do not exists"
    elif(errorCode == "EntityTemporarilyUnmodifiable"):
        error_message = "User cannot be modified"
    else:
        error_message = errorCode

    return {
        "error_message": error_message
    }