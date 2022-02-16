import jwt
import json

def hello(event, context):
    encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")

    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
        "token": str(encoded_jwt)
    }

    return {"statusCode": 200, "body": json.dumps(body)}
