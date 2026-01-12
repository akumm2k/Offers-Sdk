from http import HTTPStatus
from typing import Dict
from uuid import UUID, uuid7

import pytest
from pytest_mock import MockerFixture

from offers_sdk.client import OffersClient
from offers_sdk.config import ApiConfig
from offers_sdk.exceptions import (
    AuthenticationError,
    ServerError,
    ValidationError,
)
from offers_sdk.http.base_client import (
    BaseHttpClient,
    TokenRefreshError,
)
from offers_sdk.http.http_response import HttpResponse
from offers_sdk.models import Offers, Product


@pytest.fixture
def api_config():
    return ApiConfig(
        base_url="https://api.example.com",
        auth_endpoint="/auth",
        refresh_token="test-refresh-token",
    )


@pytest.fixture
def offers_sdk(
    api_config: ApiConfig, mock_http_client: MockHttpClient
):
    return OffersClient(api_config, http_client=mock_http_client)


class MockHttpClient(BaseHttpClient):
    async def _unauthenticated_get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        raise NotImplementedError

    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        raise NotImplementedError


@pytest.fixture
def mock_http_client() -> MockHttpClient:
    return MockHttpClient(
        base_url="https://api.example.com",
        refresh_token="test-refresh-token",
        auth_endpoint="/auth",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_data",
    [
        [],
        [
            {
                "id": str(uuid7()),
                "price": 100,
                "items_in_stock": 50,
            }
        ],
    ],
)
async def test_get_offers(
    mocker: MockerFixture,
    offers_sdk,
    mock_http_client: MockHttpClient,
    response_data,
):
    # Arrange
    product_id = uuid7()
    expected_offers = Offers.validate_python(response_data)

    http_response = HttpResponse(
        status_code=HTTPStatus.OK,
        json=response_data,
    )

    mocked_get = mocker.patch.object(
        mock_http_client, "get", return_value=http_response
    )

    # Act
    actual_offers = await offers_sdk.get_offers(product_id)

    # Assert
    assert actual_offers == expected_offers
    mocked_get.assert_called_once_with(
        f"products/{product_id}/offers"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product",
    [
        Product(name="Test Product", description="A test product"),
        Product(
            name="Another Product",
            description="Another test product",
        ),
    ],
)
async def test_register_product(
    mocker: MockerFixture,
    offers_sdk,
    mock_http_client: MockHttpClient,
    product: Product,
):
    # Arrange
    product_id = uuid7()
    response_data = {
        "id": str(product_id),
    }
    http_response = HttpResponse(
        status_code=HTTPStatus.OK,
        json=response_data,
    )
    mocked_post = mocker.patch.object(
        mock_http_client, "post", return_value=http_response
    )

    # Act
    result = await offers_sdk.register_product(product, product_id)

    # Assert
    assert result.product_id == str(product_id)
    mocked_post.assert_called_once_with(
        "products/register",
        data={**product.model_dump(), "id": str(product_id)},
    )


@pytest.mark.asyncio
async def test_get_offers_authentication_error(
    mocker: MockerFixture,
    offers_sdk,
    mock_http_client: MockHttpClient,
):
    # Arrange
    product_id = uuid7()
    http_response = HttpResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        json={"detail": "Unauthorized"},
    )

    mocker.patch.object(
        mock_http_client, "get", return_value=http_response
    )

    # Act & Assert
    with pytest.raises(
        AuthenticationError, match="Check refresh token"
    ):
        await offers_sdk.get_offers(product_id)


@pytest.mark.asyncio
async def test_get_offers_validation_error(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    mock_http_client: MockHttpClient,
):
    # Arrange
    product_id = uuid7()
    response_data = {"detail": "Validation error"}
    http_response = HttpResponse(
        status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
        json=response_data,
    )

    mocker.patch.object(
        mock_http_client, "get", return_value=http_response
    )

    # Act & Assert
    with pytest.raises(ValidationError):
        await offers_sdk.get_offers(product_id)


@pytest.mark.asyncio
async def test_get_offers_server_error(
    mocker: MockerFixture,
    offers_sdk,
    mock_http_client: MockHttpClient,
):
    # Arrange
    product_id = uuid7()
    http_response = HttpResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        json={"detail": "Internal server error"},
    )

    mocker.patch.object(
        mock_http_client, "get", return_value=http_response
    )

    # Act & Assert
    with pytest.raises(ServerError):
        await offers_sdk.get_offers(product_id)


@pytest.mark.asyncio
async def test_register_product_validation_error_conflict(
    mocker: MockerFixture,
    offers_sdk,
    mock_http_client: MockHttpClient,
):
    # Arrange
    product = Product(
        name="Test Product", description="A test product"
    )
    product_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    response_data = {"detail": "Product already exists"}
    http_response = HttpResponse(
        status_code=HTTPStatus.CONFLICT,
        json=response_data,
    )

    mocker.patch.object(
        mock_http_client, "post", return_value=http_response
    )

    # Act & Assert
    with pytest.raises(ValidationError, match="already exists"):
        await offers_sdk.register_product(product, product_id)


@pytest.mark.asyncio
async def test_token_refresh_error_handling(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    mock_http_client: MockHttpClient,
):
    # Arrange
    product_id = uuid7()

    mocker.patch.object(
        mock_http_client,
        "get",
        side_effect=TokenRefreshError(
            "Token refresh failed",
            HttpResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                json={},
            ),
        ),
    )

    # Act & Assert
    with pytest.raises(
        AuthenticationError, match="Bad authentication"
    ):
        await offers_sdk.get_offers(product_id)
