import json

import db
import utils
import utils.auth as auth

from utils import make_response
from exceptions import HandledException

class RequestHandler():

    def __init__(self, event):
        self.event = event

    def parse_request(self):
        self.body = utils.get_event_body(self.event)

        self.access_token = utils.get_body_parameter(self.body, 'access_token', required=True)
        self.name = utils.get_body_parameter(self.body, 'name', required=True)
        self.description = utils.get_body_parameter(self.body, 'description', required=False)

        return self

    def validate_request(self):
        decoded_token = auth.validate_token(self.access_token)
        self.user_id = decoded_token.get('user_id')

        return self
    
    def process(self):
        connection = db.get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO tasks (user_id, name, description) VALUES (%s, %s, %s)
        """
        try:
            cursor.execute(query, (self.user_id, self.name, self.description))
            connection.commit()

            self.result = {
                'success': True,
                'message': "Task successfuly created!",
                'task': {
                    'id': cursor.lastrowid, 
                    'user_id': self.user_id,
                    'name': self.name,
                    'description': self.description
                }
            }

            return self
        
        except Exception:
            message = "Failed to register task."
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