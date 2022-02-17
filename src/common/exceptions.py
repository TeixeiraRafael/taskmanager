class HandledException(Exception):
    """
    Abstract base class for our handled exceptions

    This class was created to enforce the idea that
    every custom exception we make needs a
    http_status and client_message attribute
    """

    def __init__(self, message, client_message, http_status):
        if not message:
            message = client_message
        super().__init__(message)
        self.http_status = http_status
        self.client_message = client_message


class InvalidRequest(HandledException):
    def __init__(self, message, client_message, http_status=403):
        super().__init__(message, client_message, http_status)
