class InvalidBearerPattern(Exception):
    pass


class InvalidTokenFormat(Exception):
    pass


class InvalidTokenHeader(Exception):
    pass


class InvalidTokenSignature(Exception):
    pass


class ExpiredToken(Exception):
    pass


class InvalidTokenCapabilities(Exception):
    pass