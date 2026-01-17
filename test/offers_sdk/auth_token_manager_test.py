from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
import pytest

from offers_sdk_applifting.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)

_SECRET_REFRESH_TOKEN = "test_refresh_token_67"


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


def test_initialization_with_invalid_stored_token(
    token_manager_stub_factory: Callable[[str], AuthTokenManager],
) -> None:
    token_manager = token_manager_stub_factory("invalid.token.string")
    assert token_manager.is_current_token_expired()


def test_token_expired_when_given_expired_token(
    expired_jwt_token: str,
    token_manager_stub_factory: Callable[[str], AuthTokenManager],
) -> None:
    token_manager = token_manager_stub_factory(expired_jwt_token)
    assert token_manager.is_current_token_expired()


def test_token_not_expired_when_given_valid_token(
    future_jwt_token: str,
    token_manager_stub_factory: Callable[[str], AuthTokenManager],
) -> None:
    token_manager = token_manager_stub_factory(future_jwt_token)
    assert not token_manager.is_current_token_expired()
