import os
import jwt
import json

from dotenv import load_dotenv

load_dotenv()
AUTH_SECRET = os.getenv('AUTH_SECRET')

def authenticate(event, context):
    encoded_jwt = jwt.encode({"some": "payload"}, AUTH_SECRET)

    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
        "token": str(encoded_jwt)
    }

    return {"statusCode": 200, "body": json.dumps(body)}