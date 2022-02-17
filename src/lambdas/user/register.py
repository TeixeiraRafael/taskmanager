import json
import bcrypt
import logging

import utils
from utils import make_response

import db
from mysql.connector import IntegrityError

from exceptions import HandledException
from email_validator import validate_email, EmailNotValidError

class RequestHandler:
    def __init__(self, event):
        self.event = event

    def parse_request(self):
        self.body = utils.get_event_body(self.event)

        self.email = utils.get_body_parameter(self.body, 'email', required=True)
        self.password = utils.get_body_parameter(self.body, 'password', required=True)
        self.username = utils.get_body_parameter(self.body, 'username', required=True)
        
        return self

    def validate_request(self):
        try:
            emailObject = validate_email(self.email)
            self.email = emailObject.email
            return self
        except EmailNotValidError as email_error:
            message = str(email_error)
            raise HandledException(message, message, 401)

    def process(self):
        self.password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt())

        query = """
            INSERT INTO users (email, password, username) VALUES (%s, %s, %s)
        """
        
        connection = db.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query, (self.email, self.password, self.username))
            connection.commit()

            self.result = {
                'success': True,
                'message': "User successfully registered!"
            }

            return self

        except IntegrityError:
            message = "An user with that email address is already registered."
            raise HandledException(message, message, 401)

    def format_response(self):
        return json.dumps(self.result)
            

def lambda_handler(event, context):
    request_handler = RequestHandler(event)
    try:
        result = request_handler.parse_request().validate_request().process().format_response()
        return make_response(result, 200)
    except HandledException as e:
        return make_response({'success': False, 'message': e.client_message}, e.http_status)