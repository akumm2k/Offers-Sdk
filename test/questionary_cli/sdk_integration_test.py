from http import HTTPStatus
from uuid import uuid7

import pytest
from pytest_mock import MockerFixture

from offers_sdk_applifting.client import OffersClient
from offers_sdk_applifting.http.base_client import BaseHttpClient
from offers_sdk_applifting.http.http_response import HttpResponse
from offers_sdk_applifting.models import Product
from questionary_cli.commands.register_product import (
    run as register_product,
)


@pytest.mark.asyncio
async def test_register_product_integration(
    offers_sdk: OffersClient,
    http_client_stub: BaseHttpClient,
    mocker: MockerFixture,
) -> None:
    # Arrange
    expected_product = Product(
        name="Test Product",
        description="This is a test product",
    )
    product_id = uuid7()
    mocker.patch.object(
        http_client_stub,
        http_client_stub.post.__name__,
        return_value=HttpResponse(
            status_code=HTTPStatus.CREATED,
            json={"id": str(product_id)},
        ),
    )

    # Simulate questionary prompt
    prompt = mocker.Mock()
    prompt.ask_async = mocker.AsyncMock(
        side_effect=[
            expected_product.name,
            expected_product.description,
        ]
    )
    mocker.patch(
        "questionary_cli.commands.register_product.questionary.text",
        return_value=prompt,
    )
    print_mock = mocker.patch(
        "questionary_cli.commands.register_product.questionary.print"
    )

    # Act
    await register_product(offers_sdk)

    print_mock.assert_called_with(
        f"✅ Product registered with ID: {product_id}",
        style="bold fg:green",
    )
