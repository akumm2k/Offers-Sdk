import pytest
from http import HTTPStatus
from http_client.requests_client import RequestsClient
import requests
from typing import Dict
from http_client.http_client import HttpClient
from pytest_mock import MockerFixture
from urllib.parse import urljoin


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: Dict = {}):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


async def no_refresh(self: HttpClient) -> None:
    return None


@pytest.fixture
def base_url() -> str:
    return "https://api.example.com/api/v1/"


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
    endpoint: str,
    params: Dict,
    headers: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    # Arrange
    mocker.patch.object(
        HttpClient, "_ensure_refresh_token", new=no_refresh
    )
    get_mock = mocker.patch.object(
        requests.Session,
        "get",
        return_value=MockResponse(expected_status, expected_json),
    )

    client = RequestsClient(
        base_url=base_url,
        refresh_token="dummy",
        auth_endpoint="auth",
    )
    resp = await client.get(endpoint, params=params, headers=headers)
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
    endpoint: str,
    data: Dict,
    headers_arg: Dict,
    expected_status: HTTPStatus,
    expected_json: Dict,
):
    def fake_session_post(
        self, url: str, json: Dict, headers: Dict
    ) -> MockResponse:
        assert url.endswith(f"/{endpoint}")
        assert json == data
        for key, value in headers.items():
            assert headers_arg.get(key) == value
        return MockResponse(expected_status, expected_json)

    mocker.patch.object(
        HttpClient, "_ensure_refresh_token", new=no_refresh
    )
    mocker.patch.object(
        requests.Session, "post", new=fake_session_post
    )

    client = RequestsClient(
        base_url="https://api.example.com",
        refresh_token="dummy",
        auth_endpoint="auth",
    )
    resp = await client.post(endpoint, data=data, headers=headers_arg)

    assert resp.status_code == expected_status
    assert resp.json == expected_json
