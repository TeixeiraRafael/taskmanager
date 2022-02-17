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
        return self

    def validate_request(self):
        decoded_token = auth.validate_token(self.access_token)
        self.user_id = decoded_token.get('user_id')
        return self

    def process(self):
        connection = db.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM tasks WHERE user_id = %s AND ISNULL(deleted_at)"

        try:
            cursor.execute(query, (self.user_id, ))
            print(cursor._executed)
            self.result = cursor.fetchall()
            return self
        except Exception as e:
            message = "Failed to retrieve tasks - " + str(e)
            raise HandledException(message, message, 401)

    def format_response(self):
        tasks = []
        for row in self.result:
            tasks.append({
                'id': row.get('id'),
                'name': row.get('name'),
                'description': row.get('description'),
                'done': row.get('done'),
                'created_at': str(row.get('created_at')),
                'updated_at': str(row.get('updated_at'))
            })
        return json.dumps({'success': True, 'tasks': tasks})

def lambda_handler(event, context):
    request_handler = RequestHandler(event)
    try:
        result = request_handler.parse_request().validate_request().process().format_response()
        return make_response(result, 200)
    except HandledException as e:
        return make_response({'message': e.client_message}, e.http_status)

    