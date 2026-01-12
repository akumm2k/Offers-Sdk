from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
import pytest

from offers_sdk.http.base_client import (
    BaseHttpClient,
    HttpResponse,
    TokenRefreshError,
    ensure_refresh_token,
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


class MockClient(BaseHttpClient):
    def __init__(
        self,
        refresh_token: str,
        auth_endpoint: str,
        future_token: str = "",
    ):
        super().__init__(
            base_url="http://testserver",
            refresh_token=refresh_token,
            auth_endpoint=auth_endpoint,
        )
        self._future_token = future_token

    @ensure_refresh_token
    async def get(
        self, endpoint: str, params: dict = {}, headers: dict = {}
    ) -> HttpResponse:
        if self._access_token is None:
            return HttpResponse(
                status_code=HTTPStatus.UNAUTHORIZED, json={}
            )
        return HttpResponse(
            status_code=HTTPStatus.OK, json={"data": "test"}
        )

    async def _unauthenticated_post(
        self, endpoint: str, data: dict = {}, headers: dict = {}
    ) -> HttpResponse:
        if endpoint != self._auth_endpoint:
            return HttpResponse(
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

    @ensure_refresh_token
    async def post(
        self, endpoint: str, data: dict = {}, headers: dict = {}
    ) -> HttpResponse:
        if self._access_token is None:
            return HttpResponse(
                status_code=HTTPStatus.UNAUTHORIZED, json={}
            )
        return HttpResponse(status_code=HTTPStatus.OK, json={})


class TestHttpClientTokenRefresh:
    @pytest.mark.asyncio
    async def test_should_refresh_expired_token(
        self, future_expiry_token: str
    ):
        # Arrange
        client = MockClient(
            refresh_token=_VALID_REFRESH_TOKEN,
            auth_endpoint="auth",
            future_token=future_expiry_token,
        )

        # Act
        await client.get("data")

        # Assert
        assert client._access_token == future_expiry_token
        assert client._token_expiry > datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_should_throw_on_invalid_refresh_token(
        self, future_expiry_token: str
    ):
        # Arrange
        client = MockClient(
            refresh_token="invalid_refresh_token",
            auth_endpoint="auth",
            future_token=future_expiry_token,
        )

        # Act & Assert
        with pytest.raises(TokenRefreshError) as exc_info:
            await client.get("data")

        assert "Failed to refresh access token" in str(exc_info.value)
