from http import HTTPStatus
from uuid import UUID, uuid7

import pytest
from pytest_mock import MockerFixture

from offers_sdk_applifting.client import OffersClient
from offers_sdk_applifting.exceptions import (
    AuthenticationError,
    SDKError,
    ServerError,
    ValidationError,
)
from offers_sdk_applifting.http.base_client import (
    BaseHttpClient,
    TokenRefreshError,
)
from offers_sdk_applifting.http.http_response import (
    HttpResponse,
    JSONType,
)
from offers_sdk_applifting.models import Offers, Product


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
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
    response_data: JSONType,
):
    # Arrange
    product_id = uuid7()
    expected_offers = Offers.validate_python(response_data)

    http_response = HttpResponse(
        status_code=HTTPStatus.OK,
        json=response_data,
    )

    mocked_get = mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
        return_value=http_response,
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
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
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
        http_client_stub,
        http_client_stub.post.__name__,
        return_value=http_response,
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
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
):
    # Arrange
    product_id = uuid7()
    http_response = HttpResponse(
        status_code=HTTPStatus.UNAUTHORIZED,
        json={"detail": "Unauthorized"},
    )

    mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
        return_value=http_response,
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
    http_client_stub: BaseHttpClient,
):
    # Arrange
    product_id = uuid7()
    response_data = {"detail": "Validation error"}
    http_response = HttpResponse(
        status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
        json=response_data,
    )

    mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
        return_value=http_response,
    )

    # Act & Assert
    with pytest.raises(ValidationError):
        await offers_sdk.get_offers(product_id)


@pytest.mark.asyncio
async def test_get_offers_server_error(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
):
    # Arrange
    product_id = uuid7()
    http_response = HttpResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        json={"detail": "Internal server error"},
    )

    mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
        return_value=http_response,
    )

    # Act & Assert
    with pytest.raises(ServerError):
        await offers_sdk.get_offers(product_id)


@pytest.mark.asyncio
async def test_register_product_validation_error_conflict(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
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
        http_client_stub,
        http_client_stub.post.__name__,
        return_value=http_response,
    )

    # Act & Assert
    with pytest.raises(ValidationError, match="already exists"):
        await offers_sdk.register_product(product, product_id)


@pytest.mark.asyncio
async def test_token_refresh_error_handling(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
):
    # Arrange
    product_id = uuid7()

    mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
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


@pytest.mark.asyncio
async def test_unexpected_api_error_handling(
    mocker: MockerFixture,
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
):
    # Arrange
    product_id = uuid7()

    mocker.patch.object(
        http_client_stub,
        http_client_stub.get.__name__,
        return_value=HttpResponse(
            status_code=HTTPStatus.IM_A_TEAPOT,
            json={},
        ),
    )

    # Act & Assert
    with pytest.raises(SDKError, match="Unexpected error"):
        await offers_sdk.get_offers(product_id)
