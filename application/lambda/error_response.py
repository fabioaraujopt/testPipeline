import json
from collections import namedtuple

ErrorCodeTuple = namedtuple('ErrorCode', ['message', 'status_code'])

known_error_codes = {
    'AccessDenied': ErrorCodeTuple('Access denied for account', 403),
    'EntityAlreadyExists': ErrorCodeTuple('Username already exists', 400),
    'NoSuchEntity': ErrorCodeTuple('Username not found', 404),
    'EntityTemporarilyUnmodifiable': ErrorCodeTuple('User cannot be modified', 409)
}


def error_response(exception):
    exception = exception.response['Error']['Code']

    try:
        error_code = known_error_codes[exception]
    except KeyError:
        error_code = ErrorCodeTuple(exception, 500)

    return {
        'statusCode': error_code.status_code,
        'body': json.dumps({
            "message": error_code.message
        })
    }
