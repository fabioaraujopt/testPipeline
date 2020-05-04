import json
from collections import namedtuple

ErrorCodeTuple = namedtuple('ErrorCode', ['message', 'status_code'])

# todo change string
known_error_codes = {
    'AccessDenied': ErrorCodeTuple('AWS denied action for this account.', 403),
    'EntityTemporarilyUnmodifiable': ErrorCodeTuple(
        'AWS couldn\' could not perform this action at the \
             moment. Please try again later.', 409
    )
}


def error_response(exception):
    exception = exception.response['Error']['Code']

    # check contains
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
