"""Domain Exceptions for the SDK"""


class SDKError(Exception):
    pass


class ServerError(SDKError):
    pass


class AuthenticationError(SDKError):
    pass


class ValidationError(SDKError):
    pass
