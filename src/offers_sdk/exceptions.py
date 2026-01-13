from typing import Optional

from offers_sdk.http.base_client import HttpResponse


class SDKError(Exception):
    def __init__(
        self,
        msg: str,
        http_response: Optional[HttpResponse] = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        if http_response:
            msg = "\n".join(
                [
                    msg,
                    f"with {http_response}",
                ]
            )
        super().__init__(msg, *args, **kwargs)


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
