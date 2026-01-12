"""Domain Exceptions for the SDK"""


class ServerError(Exception):
    """
    Exception raised for server-side errors (5xx HTTP status codes).
    """

    pass


class AuthenticationError(Exception):
    """
    Exception for authentication failures.
    """

    pass


class ValidationError(Exception):
    """
    Exception for Server-side validation errors.
    For example, server not being able to process the request.
    """

    pass
