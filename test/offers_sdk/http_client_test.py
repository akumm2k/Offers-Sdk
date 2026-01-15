from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
import pytest
from pytest_mock import MockerFixture

from offers_sdk.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk.http.base_client import (
    BaseHttpClient,
    HttpResponse,
    TokenRefreshError,
)

_VALID_REFRESH_TOKEN = "secret_refresh_token"


@pytest.fixture
def future_expiry_token() -> str:
    future_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"expires": future_expiry.timestamp()},
        _VALID_REFRESH_TOKEN,
        algorithm="HS256",
    )
    return token


@pytest.fixture
def expired_token() -> str:
    past_expiry = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {"expires": past_expiry.timestamp()},
        _VALID_REFRESH_TOKEN,
        algorithm="HS256",
    )
    return token


class MockTokenManager(AuthTokenManager):
    def __init__(self, get_token_value: str) -> None:
        self._get_token_value = get_token_value
        super().__init__()

    def get_token(self) -> str:
        return self._get_token_value

    def store_token(self, token: str) -> None:
        pass


class MockClient(BaseHttpClient):
    def __init__(
        self,
        refresh_token: str,
        auth_endpoint: str,
        future_token: str,
        token_manager: AuthTokenManager,
    ):
        super().__init__(
            base_url="http://testserver",
            refresh_token=refresh_token,
            auth_endpoint=auth_endpoint,
            token_manager=token_manager,
        )
        self._future_token = future_token

    async def _unauthenticated_get(
        self, endpoint: str, params: dict = {}, headers: dict = {}
    ) -> HttpResponse:
        if self._token_manager.is_current_token_expired():
            return HttpResponse(  # pragma: no cover
                status_code=HTTPStatus.UNAUTHORIZED, json={}
            )
        return HttpResponse(
            status_code=HTTPStatus.OK, json={"data": "test"}
        )

    async def _unauthenticated_post(
        self, endpoint: str, data: dict = {}, headers: dict = {}
    ) -> HttpResponse:
        # auth only post
        if endpoint != self._auth_endpoint:
            return HttpResponse(  # pragma: no cover
                status_code=HTTPStatus.NOT_FOUND, json={}
            )
        if self._refresh_token != _VALID_REFRESH_TOKEN:
            return HttpResponse(
                status_code=HTTPStatus.UNAUTHORIZED, json={}
            )
        return HttpResponse(
            status_code=HTTPStatus.CREATED,
            json={"access_token": self._future_token},
        )


class TestHttpClientTokenRefresh:
    @pytest.mark.asyncio
    async def test_should_refresh_missing_auth_token(
        self,
        future_expiry_token: str,
    ):
        # Arrange
        token_manager = MockTokenManager(get_token_value="")
        client = MockClient(
            refresh_token=_VALID_REFRESH_TOKEN,
            auth_endpoint="auth",
            future_token=future_expiry_token,
            token_manager=token_manager,
        )

        # Act
        data = await client.get("data")

        # Assert
        assert data.status_code == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_should_refresh_expired_auth_token(
        self,
        future_expiry_token: str,
        expired_token: str,
    ):
        # Arrange
        token_manager = MockTokenManager(
            get_token_value=expired_token
        )
        client = MockClient(
            refresh_token=_VALID_REFRESH_TOKEN,
            auth_endpoint="auth",
            future_token=future_expiry_token,
            token_manager=token_manager,
        )

        # Act
        data = await client.get("data")

        # Assert
        assert data.status_code == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_should_not_refresh_valid_auth_token(
        self,
        future_expiry_token: str,
        mocker: MockerFixture,
    ):
        # Arrange
        token_manager = MockTokenManager(
            get_token_value=future_expiry_token
        )
        mocker.patch.object(
            token_manager,
            AuthTokenManager.get_token.__name__,
            return_value=future_expiry_token,
        )
        client = MockClient(
            refresh_token=_VALID_REFRESH_TOKEN,
            auth_endpoint="auth",
            future_token=future_expiry_token,
            token_manager=token_manager,
        )

        # Act
        data = await client.get("data")

        # Assert
        assert data.status_code == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_should_throw_on_invalid_refresh_token(
        self,
        future_expiry_token: str,
    ):
        # Arrange
        token_manager = MockTokenManager(get_token_value="")
        client = MockClient(
            refresh_token="invalid_refresh_token",
            auth_endpoint="auth",
            future_token=future_expiry_token,
            token_manager=token_manager,
        )

        # Act & Assert
        with pytest.raises(TokenRefreshError) as exc_info:
            await client.get("data")

        assert "Failed to refresh access token" in str(exc_info.value)
