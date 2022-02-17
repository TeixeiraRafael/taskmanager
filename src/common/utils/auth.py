import os
import jwt
import json
from exceptions import HandledException

from dotenv import load_dotenv

load_dotenv()
AUTH_SECRET = os.getenv('AUTH_SECRET')

def sign_token(payload):
    encoded_jwt = jwt.encode(payload, AUTH_SECRET)
    return encoded_jwt.decode("utf-8")

def validate_token(token):
    try:
        return jwt.decode(token, AUTH_SECRET)
    except Exception as e:
        message = "Failed to validate token: " + str(e)
        raise HandledException(message, message, 403)