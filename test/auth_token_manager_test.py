from datetime import datetime, timedelta, timezone

import jwt
import pytest

from offers_sdk.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)

_SECRET_REFRESH_TOKEN = "test_refresh_token_67"


class MockTokenManager(AuthTokenManager):
    def __init__(self, fake_get_token: str) -> None:
        self._fake_get_token = fake_get_token
        super().__init__()

    def get_token(self) -> str:
        return self._fake_get_token

    def store_token(self, token: str) -> None:
        pass


@pytest.fixture
def future_jwt_token() -> str:
    future_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"expires": future_expiry.timestamp()},
        _SECRET_REFRESH_TOKEN,
        algorithm="HS256",
    )
    return token


@pytest.fixture
def expired_jwt_token() -> str:
    past_expiry = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {"expires": past_expiry.timestamp()},
        _SECRET_REFRESH_TOKEN,
        algorithm="HS256",
    )
    return token


def test_initialization_with_invalid_stored_token() -> None:
    token_manager = MockTokenManager("invalid.token.string")
    assert token_manager.is_current_token_expired()


def test_token_expired_when_given_expired_token(
    expired_jwt_token: str,
) -> None:
    token_manager = MockTokenManager(expired_jwt_token)
    assert token_manager.is_current_token_expired()


def test_token_not_expired_when_given_valid_token(
    future_jwt_token: str,
) -> None:
    token_manager = MockTokenManager(future_jwt_token)
    assert not token_manager.is_current_token_expired()
