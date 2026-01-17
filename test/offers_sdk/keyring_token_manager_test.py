"""Unit tests for KeyringTokenManager."""

from datetime import datetime, timedelta, timezone

import jwt
import keyring
import pytest
from pytest_mock import MockerFixture

from offers_sdk_applifting.http.auth_token.keyring_token_manager import (
    KeyringTokenManager,
)

_SECRET_SERVICE_KEY = "test_secret_key"
_TOKEN_KEY = "test_token_key"


@pytest.fixture
def valid_token() -> str:
    future_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"expires": future_expiry.timestamp()},
        _SECRET_SERVICE_KEY,
        algorithm="HS256",
    )
    return token


def test_get_token_returns_stored_token(
    mocker: MockerFixture, valid_token: str
) -> None:
    # Arrange
    mocker.patch.object(
        keyring,
        keyring.get_password.__name__,
        return_value=valid_token,
    )
    token_mgr = KeyringTokenManager(_TOKEN_KEY)

    # Act
    retrieved_token = token_mgr.get_token()

    # Assert
    assert retrieved_token == valid_token


def test_store_token_saves_to_keyring(mocker: MockerFixture) -> None:
    # Arrange
    set_password_mock = mocker.patch.object(
        keyring,
        keyring.set_password.__name__,
    )
    token_mgr = KeyringTokenManager(_TOKEN_KEY)
    test_token = "sample_token_456"

    # Act
    token_mgr.set_token(test_token)

    # Assert
    set_password_mock.assert_called_once_with(
        KeyringTokenManager._KEYRING_SERVICE_NAME,
        _TOKEN_KEY,
        test_token,
    )
