from http import HTTPStatus

import pytest

from offers_sdk_applifting.exceptions import SDKError
from offers_sdk_applifting.http.http_response import HttpResponse


@pytest.mark.parametrize(
    "http_response",
    [
        HttpResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            json={"error": "Unauthorized"},
        ),
        HttpResponse(
            status_code=HTTPStatus.FORBIDDEN,
            json={"error": "Forbidden"},
        ),
    ],
)
def test_exception_msg_includes_http_response(
    http_response: HttpResponse,
):
    # Arrange
    error_message = "Authentication failed"

    # Act
    with pytest.raises(SDKError) as exc_info:
        raise SDKError(error_message, http_response)

    # Assert
    assert str(http_response) in exc_info.value.args[0]


def test_exception_without_http_response():
    # Arrange
    error_message = "An error occurred"

    # Act
    with pytest.raises(SDKError) as exc_info:
        raise SDKError(error_message)

    # Assert
    assert exc_info.value.args[0] == error_message
