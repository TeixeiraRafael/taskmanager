import json
import time
import datetime 

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
        
        self.task_id = utils.get_body_parameter(self.body, 'id', required=True)
        self.name = utils.get_body_parameter(self.body, 'name', required=True)
        self.description = utils.get_body_parameter(self.body, 'description', required=True)
        self.done = utils.get_body_parameter(self.body, 'done', required=True)
        return self

    def validate_request(self):
        decoded_token = auth.validate_token(self.access_token)
        self.user_id = decoded_token.get('user_id')
        
        return self
    
    def process(self):
        connection = db.get_connection()
        cursor = connection.cursor()

        query = """
            UPDATE tasks 
            SET name = %s, description = %s, done = %s, updated_at = %s
            WHERE id = %s AND ISNULL(deleted_at) AND user_id = %s
        """

        try:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(query, (
                self.name,
                self.description,
                int(self.done),
                timestamp,
                self.task_id,
                self.user_id
            ))
            connection.commit()
            if cursor.rowcount  == 0:
                raise Exception

            self.result = {
                'success': True,
                'message': "Task successfuly updated!",
                'task': {
                    'id': self.task_id, 
                    'user_id': self.user_id,
                    'name': self.name,
                    'description': self.description,
                    'done': self.done,
                    'updated_at': timestamp
                }
            }

            return self
        except Exception:
            message = "Failed to update task"
            raise HandledException(message, message, 401)
    
    def format_response(self):
        return json.dumps(self.result)

def lambda_handler(event, context):
    request_handler = RequestHandler(event)
    try:
        result = request_handler.parse_request().validate_request().process().format_response()
        return make_response(result, 200)
    except HandledException as e:
        return make_response({'message': e.client_message}, e.http_status)