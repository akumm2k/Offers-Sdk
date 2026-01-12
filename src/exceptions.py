"""Domain Exceptions for the SDK"""

from http_client.base_client import HttpResponse


class SDKError(Exception):
    def __init__(
        self, msg: str, http_response: HttpResponse, *args: object
    ) -> None:
        self.http_response = http_response

        msg_with_status = f"{msg}\nHTTP Status: {http_response.status_code}\nResponse JSON: {http_response.json}"
        super().__init__(msg_with_status, *args)


class ServerError(SDKError):
    """
    Exception raised for server-side errors (5xx HTTP status codes).
    """

    pass


class AuthenticationError(SDKError):
    """
    Exception for authentication failures.
    """

    pass


class ValidationError(SDKError):
    """
    Exception for Server-side validation errors.
    For example, server not being able to process the request.
    """

    pass
