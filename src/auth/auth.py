import os
import jwt
import json

import utils.testutil as testutil
import db.testdb as testdb

from dotenv import load_dotenv

load_dotenv()
AUTH_SECRET = os.getenv('AUTH_SECRET')

def authenticate(event, context):
    #extract user + password
    #validate on the database
    #sign token
    #return

    encoded_jwt = jwt.encode({"some": "payload"}, AUTH_SECRET)

    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "testutil": testutil.hello(),
        "testdb": testdb.test(),
        "token": str(encoded_jwt)
    }

    return {"statusCode": 200, "body": json.dumps(body)}