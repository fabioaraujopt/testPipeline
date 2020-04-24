import base64
import datetime
import json
import re

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

import rds_exceptions

def pad_base64(unpadded_base64, is_bytes=False):
    '''
    In base64, the length of the encoded data must be multiple of 4
    '''
    missing_padding = len(unpadded_base64) % 4
    if missing_padding == 1:
        if is_bytes:
            return unpadded_base64 + b'A=='
        return unpadded_base64 + 'A=='
    elif missing_padding == 2:
        if is_bytes:
            return unpadded_base64 + b'=='
        return unpadded_base64 + '=='
    elif missing_padding == 3:
        if is_bytes:
            return unpadded_base64 + b'='
        return unpadded_base64 + '='
    return unpadded_base64


def unwrap_token_parts(token_part, json_loads=True, is_bytes=False):
    unwrapped_token_part = base64.urlsafe_b64decode(
        pad_base64(
            token_part,
            is_bytes=is_bytes,
        ),
    )
    if json_loads:
        return json.loads(unwrapped_token_part)
    return unwrapped_token_part


def validate_token(raw_token, public_key, required_capabilities):
    jwt_token = JWTtoken(raw_token, public_key)
    jwt_token.verify_bearer_pattern()
    jwt_token.split_token()
    jwt_token.validate_header()
    jwt_token.validate_signature()
    jwt_token.validate_expiry_date()
    jwt_token.validate_capabilities(required_capabilities)


class JWTtoken:
    def __init__(self, raw_token, public_key):
        self.raw_token = raw_token
        public_key = public_key.encode('utf-8')
        self.public_key = load_pem_public_key(
            public_key,
            backend=default_backend(),
        )

    def verify_bearer_pattern(self):
        pattern = "Bearer .*"
        if re.match(pattern, self.raw_token):
            return
        raise rds_exceptions.InvalidBearerPattern(
            f"Invalid token BEARER pattern. Raw token: {self.raw_token}",
        )

    def split_token(self):
        token_without_bearer = self.raw_token[7:]
        splitted_token = token_without_bearer.split(".")
        if len(splitted_token) != 3:
            raise rds_exceptions.InvalidTokenFormat(
                f"Token must be composed by 3 parts delimited by a '.'."
                f" Raw token: {self.raw_token}",
            )
        self.header = splitted_token[0]
        self.payload = splitted_token[1]
        self.signature = splitted_token[2]

    def validate_header(self):
        decoded_header = unwrap_token_parts(self.header)
        if decoded_header["typ"] == "JWT" and decoded_header["alg"] == "RS512":
            return
        raise rds_exceptions.InvalidTokenHeader(
            f"Incorrect token type or encryption algorithm."
            f" Decoded Token header: {self.decoded_header}",
        )

    def validate_signature(self):
        token_without_bearer = self.raw_token[7:]
        token_without_bearer = token_without_bearer.encode('utf-8')
        signing_input, signature = token_without_bearer.rsplit(b'.', 1)
        unwrapped_signature = unwrap_token_parts(
            signature,
            json_loads=False,
            is_bytes=True,
        )
        try:
            self.public_key.verify(
                unwrapped_signature,
                signing_input,
                padding.PKCS1v15(),
                hashes.SHA512(),
            )
        except: # noqa
            raise rds_exceptions.InvalidTokenSignature(
                "Deciphered token signature does not match payload + header.",
            )

    def validate_expiry_date(self):
        payload = unwrap_token_parts(self.payload)
        expiry_date = (payload["exp"])
        expiry_date = datetime.datetime.strptime(
            expiry_date,
            '%Y-%m-%d %H:%M:%S',
        )
        now = datetime.datetime.utcnow()
        if now > expiry_date:
            raise rds_exceptions.ExpiredToken(
                "The token validity has expired.",
            )

    def validate_capabilities(self, required_capabilities):
        payload = unwrap_token_parts(self.payload)
        token_scope = str(payload["scope"])
        for required_capability in required_capabilities:
            pattern = ''.join([".*", required_capability, ".*"])
            if not re.match(pattern, token_scope):
                raise rds_exceptions.InvalidTokenCapabilities(
                    f"Token scope does not match required capabilities."
                    f" Token scope: {token_scope}."
                    f" Required capabilities: {required_capabilities}",
                )