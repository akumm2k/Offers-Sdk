from http import HTTPStatus
from typing import Dict
from urllib.parse import urljoin

import pytest
import requests_mock
from pytest_mock import MockerFixture

from offers_sdk_applifting.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk_applifting.http.base_client import BaseHttpClient
from offers_sdk_applifting.http.requests_client import RequestsClient


@pytest.fixture
def base_url() -> str:
    return "https://api.example.com/api/v1/"


@pytest.fixture
def token_manager(mocker: MockerFixture) -> AuthTokenManager:
    return mocker.Mock(spec=AuthTokenManager)


@pytest.fixture
def requests_client(
    base_url: str, token_manager: AuthTokenManager
) -> RequestsClient:
    return RequestsClient(
        base_url=base_url,
        refresh_token="dummy",
        auth_endpoint="auth",
        token_manager=token_manager,
        backend="memory",
    )


_GET_TEST_CASES = [
    (
        "offers",
        {"q": "abc"},
        {"X-Test": "1"},
        HTTPStatus.OK,
        {"ok": True},
    ),
    (
        "products",
        {"limit": "10"},
        {"X-Custom": "value"},
        HTTPStatus.OK,
        {"data": "success"},
    ),
    (
        "offers",
        {},
        {},
        HTTPStatus.TOO_MANY_REQUESTS,
        {"error": "rate limit"},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint,params,headers,expected_status,expected_json",
    _GET_TEST_CASES,
)
async def test_get(
    mocker: MockerFixture,
    base_url: str,
    requests_client: RequestsClient,
    token_manager: AuthTokenManager,
    endpoint: str,
    params: Dict,
    headers: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    # Arrange
    mocker.patch.object(
        token_manager,
        AuthTokenManager.is_current_token_expired.__name__,
        return_value=False,
    )

    with requests_mock.Mocker() as m:
        m.get(
            urljoin(base_url, endpoint),
            status_code=expected_status,
            json=expected_json,
        )

        # Act
        resp = await requests_client.get(
            endpoint, params=params, headers=headers
        )

        # Assert
        assert resp.status_code == expected_status
        assert resp.json == expected_json


_POST_TEST_CASES = [
    (
        "offers",
        {"name": "New Offer"},
        {"Authorization": "Bearer token"},
        HTTPStatus.CREATED,
        {"id": "123"},
    ),
    (
        "products",
        {"title": "Product A", "price": 99.99},
        {"X-API-Key": "secret"},
        HTTPStatus.OK,
        {"status": "created"},
    ),
    (
        "offers",
        {},
        {},
        HTTPStatus.BAD_REQUEST,
        {"error": "invalid data"},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint,data,headers_arg,expected_status,expected_json",
    _POST_TEST_CASES,
)
async def test_post(
    mocker: MockerFixture,
    base_url: str,
    requests_client: RequestsClient,
    token_manager: AuthTokenManager,
    endpoint: str,
    data: Dict,
    headers_arg: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    # Arrange
    mocker.patch.object(
        token_manager,
        AuthTokenManager.is_current_token_expired.__name__,
        return_value=False,
    )

    with requests_mock.Mocker() as m:
        m.post(
            urljoin(base_url, endpoint),
            status_code=expected_status,
            json=expected_json,
        )

        # Act
        resp = await requests_client.post(
            endpoint, data=data, headers=headers_arg
        )

        # Assert
        assert resp.status_code == expected_status
        assert resp.json == expected_json


@pytest.mark.asyncio
async def test_auth_is_not_cached(
    requests_client: RequestsClient,
    base_url: str,
):
    with requests_mock.Mocker() as m:
        m.post(
            urljoin(base_url, "auth"), json={"access_token": "token"}
        )

        r1 = await requests_client.post("auth")
        assert r1.from_cache is False

        r2 = await requests_client.post("auth")
        assert r2.from_cache is False


@pytest.mark.asyncio
async def test_other_endpoints_are_cached(
    requests_client: RequestsClient,
    base_url: str,
):
    with requests_mock.Mocker() as m:
        m.get(
            urljoin(base_url, "data"),
            json={"value": 42},
        )
        m.post(
            urljoin(base_url, "auth"), json={"access_token": "token"}
        )

        r1 = await requests_client.get("data")
        assert r1.from_cache is False

        r2 = await requests_client.get("data")
        assert r2.from_cache is True


@pytest.mark.asyncio
async def test_cached_item_headers_are_redacted(
    requests_client: RequestsClient,
    base_url: str,
    mocker: MockerFixture,
    token_manager: AuthTokenManager,
):
    # Arrange
    mocker.patch.object(
        token_manager,
        AuthTokenManager.is_current_token_expired.__name__,
        return_value=False,
    )
    endpoint = "data"
    secret_headers = {
        BaseHttpClient._ACCESS_TOKEN_HEADER_KEY: "sensitive-token",
        BaseHttpClient._REFRESH_TOKEN_HEADER_KEY: "sensitive-token",
    }
    with requests_mock.Mocker() as mock:
        mock.get(urljoin(base_url, endpoint), json={"value": 42})

        # Act
        resp1 = await requests_client.get(
            endpoint, headers=secret_headers
        )
        resp2 = await requests_client.get(
            endpoint, headers=secret_headers
        )
        cached_responses = list(
            requests_client._session.cache.responses.values()
        )

        # Assert
        assert len(cached_responses) == 1
        cached_response = cached_responses[0]
        assert resp1.from_cache is False and resp2.from_cache is True
        assert cached_response.from_cache is True
        for secret_header in secret_headers.keys():
            assert (
                cached_response.request.headers[secret_header]
                == "REDACTED"
            )
