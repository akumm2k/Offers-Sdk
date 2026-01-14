from http import HTTPStatus
from typing import Dict
from urllib.parse import urljoin

import pytest
import requests
from pytest_mock import MockerFixture

from offers_sdk.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk.http.base_client import BaseHttpClient
from offers_sdk.http.http_response import JSONType
from offers_sdk.http.requests_client import RequestsClient


class MockResponse:
    def __init__(
        self,
        status_code: HTTPStatus = HTTPStatus.OK,
        json_data: JSONType = {},
    ):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


async def no_refresh(self: BaseHttpClient) -> None:
    return None


@pytest.fixture
def base_url() -> str:
    return "https://api.example.com/api/v1/"


@pytest.fixture
def requests_client(
    base_url: str, mocker: MockerFixture
) -> RequestsClient:
    return RequestsClient(
        base_url=base_url,
        refresh_token="dummy",
        auth_endpoint="auth",
        token_manager=mocker.Mock(spec=AuthTokenManager),
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
    endpoint: str,
    params: Dict,
    headers: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    # Arrange
    mocker.patch.object(
        BaseHttpClient, "_ensure_refresh_token", new=no_refresh
    )
    get_mock = mocker.patch.object(
        requests.Session,
        "get",
        return_value=MockResponse(expected_status, expected_json),
    )

    # Act
    resp = await requests_client.get(
        endpoint, params=params, headers=headers
    )

    # Assert
    get_mock.assert_called_once_with(
        urljoin(base_url, endpoint),
        params=params,
        headers=headers,
    )
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
    endpoint: str,
    data: Dict,
    headers_arg: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    # Arrange
    mocker.patch.object(
        BaseHttpClient, "_ensure_refresh_token", new=no_refresh
    )
    post_mock = mocker.patch.object(
        requests.Session,
        "post",
        return_value=MockResponse(expected_status, expected_json),
    )

    # Act
    resp = await requests_client.post(
        endpoint, data=data, headers=headers_arg
    )

    # Assert
    post_mock.assert_called_once_with(
        urljoin(base_url, endpoint),
        json=data,
        headers=headers_arg,
    )
    assert resp.status_code == expected_status
    assert resp.json == expected_json
