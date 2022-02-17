import os
import jwt
import json
import bcrypt

from dotenv import load_dotenv

import db

import utils
import utils.auth as auth

from utils import make_response
from exceptions import HandledException

load_dotenv()
AUTH_SECRET = os.getenv('AUTH_SECRET')

class RequestHandler():

    def __init__(self, event):
        self.event = event    

    def parse_request(self):
        self.body = utils.get_event_body(self.event)

        self.email = utils.get_body_parameter(self.body, 'email', required=True)
        self.password = utils.get_body_parameter(self.body, 'password', required=True)

        return self

    def verify_password(self):
        plain = self.password.encode()
        hashed = self.user.get('password').encode()

        if bcrypt.checkpw(plain, hashed):
            return True
        else:
            message = "Wrong username or password."
            raise HandledException(message, message, 401)

    def get_access_token(self):
        payload = {"user_id": self.user.get('id')}
        return auth.sign_token(payload)
    
    def process(self):
        connection = db.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM users WHERE email = %s;
        """

        cursor.execute(query, (self.email, ))
        result = cursor.fetchone()
        
        if not result:
            message = "Wrong username or password"
            raise HandledException(message, message, 401)

        self.user = result
        self.verify_password()

        self.result = {
            'success': True,
            'access_token': self.get_access_token()
        }

        return self

    def format_response(self):
        return(json.dumps(self.result))

def lambda_handler(event, context):
    request_handler = RequestHandler(event)
    try:
        result = request_handler.parse_request().process().format_response()
        return make_response(result, 200)
    except HandledException as e:
        return make_response({'success': False, 'message': e.client_message}, e.http_status)