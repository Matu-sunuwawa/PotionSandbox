import hashlib
import hmac
import random
import re
import secrets
import string

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key


def randomString(length=16):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits

    choice = upper + num + lower
    result = "".join(random.choice(choice) for i in range(length))

    return result


def generate_string():
    pass


def hash256(msg):
    return hashlib.sha256(str.encode(msg)).hexdigest()


def hmac_sha256(msg):
    secret_key_bytes = secrets.encode("utf-8")

    message_bytes = msg.encode("utf-8")

    hmacsha256 = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256)

    hex_digest = hmacsha256.hexdigest()

    return hex_digest


def generate_secure_six_digits():
    return secrets.randbelow(900000) + 100000