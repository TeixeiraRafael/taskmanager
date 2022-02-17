import json
import exceptions

def get_event_body(event) -> dict:
    if "body" not in event:
        message = "Event body not found."
        raise exceptions.InvalidRequest(message, message)

    if isinstance(event["body"], str):
        return get_parsed_event_body(event)

    return event["body"]

def get_parsed_event_body(event):
    try:
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        return body
    except json.JSONDecodeError as e:
        message = f"JSON decoding of event body failed: {e}"
        raise exceptions.InvalidRequest(message, message)

def get_body_parameter(body, parameter, required=False):
    value = body.get(parameter, None)

    if value == None and required:
        message = f"Validation error, missing {parameter} field"
        raise exceptions.InvalidRequest(message, message, http_status=401)
    
    return value


def make_response(body, status_code=200, content_type="application/json"):
    body = (
        body
        if isinstance(body, str)
        else json.dumps(body)
    )
    response = {
        "statusCode": str(status_code),
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": body,
    }
    if content_type:
        response["headers"]["Content-Type"] = str(content_type)
    return response
