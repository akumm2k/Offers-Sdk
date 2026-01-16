from typing import Dict

import pytest
from pytest_mock import MockerFixture

from offers_sdk_applifting.client import OffersClient
from offers_sdk_applifting.config import ApiConfig
from offers_sdk_applifting.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk_applifting.http.base_client import BaseHttpClient
from offers_sdk_applifting.http.http_response import HttpResponse


@pytest.fixture
def api_config():
    return ApiConfig(
        base_url="https://api.example.com",
        auth_endpoint="/auth",
        refresh_token="test-refresh-token",
        persistent_auth_token_key="",
    )


@pytest.fixture
def offers_sdk(
    api_config: ApiConfig, http_client_stub: HttpClientStub
) -> OffersClient:
    return OffersClient(api_config, http_client=http_client_stub)


class HttpClientStub(BaseHttpClient):
    """
    We patch the get and post methods in tests, so these are not implemented.
    """

    async def _unauthenticated_get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        raise NotImplementedError  # pragma: no cover

    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        raise NotImplementedError  # pragma: no cover


@pytest.fixture
def http_client_stub(
    api_config: ApiConfig, mocker: MockerFixture
) -> HttpClientStub:
    return HttpClientStub(
        base_url=api_config.base_url,
        refresh_token=api_config.refresh_token,
        auth_endpoint=api_config.auth_endpoint,
        token_manager=mocker.Mock(spec=AuthTokenManager),
    )
