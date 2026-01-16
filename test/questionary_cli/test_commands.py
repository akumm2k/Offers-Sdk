from unittest.mock import Mock
from uuid import UUID, uuid7

import pytest
import questionary
from pytest_mock import MockerFixture

from offers_sdk.client import OffersClient
from offers_sdk.exceptions import ValidationError
from offers_sdk.models import Offer, Product
from questionary_cli.commands.get_offers import print_offers_table
from questionary_cli.commands.get_offers import run as get_offers
from questionary_cli.commands.register_product import (
    run as register_product,
)


@pytest.fixture
def offers_sdk_mock(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=OffersClient)


@pytest.mark.asyncio
async def test_register_product_success2(
    mocker: MockerFixture, offers_sdk_mock: Mock
) -> None:
    expected_product = Product(
        name="Test Product", description="This is a test product."
    )
    print_mock = mocker.patch.object(questionary, "print")
    prompts_mocks = Mock()
    prompts_mocks.ask_async = mocker.AsyncMock(
        side_effect=[
            expected_product.name,
            expected_product.description,
        ]
    )

    mocker.patch.object(
        questionary,
        questionary.text.__name__,
        return_value=prompts_mocks,
    )

    offers_sdk_mock.register_product = mocker.AsyncMock(
        return_value=Mock(product_id="12345")
    )

    await register_product(offers_sdk_mock)

    offers_sdk_mock.register_product.assert_awaited_once_with(
        expected_product
    )
    print_mock.assert_called_with(
        "✅ Product registered with ID: 12345", style="bold fg:green"
    )


@pytest.mark.asyncio
async def test_register_product_failure(
    mocker: MockerFixture, offers_sdk_mock: Mock
) -> None:
    expected_product = Product(
        name="Test Product", description="This is a test product."
    )
    print_mock = mocker.patch.object(questionary, "print")
    prompts_mock = Mock()
    prompts_mock.ask_async = mocker.AsyncMock(
        side_effect=[
            expected_product.name,
            expected_product.description,
        ]
    )

    mocker.patch.object(
        questionary,
        questionary.text.__name__,
        return_value=prompts_mock,
    )

    offers_sdk_mock.register_product = mocker.AsyncMock(
        side_effect=ValidationError(
            f"Product with ID {expected_product.name} already exists",
        )
    )

    await register_product(offers_sdk_mock)

    offers_sdk_mock.register_product.assert_awaited_once_with(
        expected_product
    )
    print_mock.assert_called_with(
        f"❌ Failed to register product: "
        f"Product with ID {expected_product.name} already exists",
        style="bold fg:red",
    )


@pytest.mark.asyncio
async def test_get_offers_no_offers(
    mocker: MockerFixture, offers_sdk_mock: Mock
) -> None:
    product_id = str(uuid7())
    prompts_mock = Mock()
    prompts_mock.ask_async = mocker.AsyncMock(return_value=product_id)

    mocker.patch.object(
        questionary,
        questionary.text.__name__,
        return_value=prompts_mock,
    )

    offers_sdk_mock.get_offers = mocker.AsyncMock(return_value=[])

    print_mock = mocker.patch.object(questionary, "print")

    await get_offers(offers_sdk_mock)

    offers_sdk_mock.get_offers.assert_awaited_once_with(
        UUID(product_id)
    )
    print_mock.assert_called_once_with(
        "No offers found for this product."
    )


@pytest.mark.asyncio
async def test_get_offers_with_offers(
    mocker: MockerFixture, offers_sdk_mock: Mock
) -> None:
    product_id = str(uuid7())
    prompts_mock = Mock()
    prompts_mock.ask_async = mocker.AsyncMock(return_value=product_id)

    mocker.patch.object(
        questionary,
        questionary.text.__name__,
        return_value=prompts_mock,
    )

    expected_offers = [
        Mock(id=uuid7(), price=19.99, items_in_stock=10),
        Mock(id=uuid7(), price=29.99, items_in_stock=5),
    ]
    offers_sdk_mock.get_offers = mocker.AsyncMock(
        return_value=expected_offers
    )

    print_table_mock = mocker.patch(
        "questionary_cli.commands.get_offers.print_offers_table"
    )

    await get_offers(offers_sdk_mock)

    offers_sdk_mock.get_offers.assert_awaited_once_with(
        UUID(product_id)
    )
    print_table_mock.assert_called_once_with(expected_offers)


def test_print_offers_table(
    mocker: MockerFixture,
) -> None:
    offers = [
        Offer(id=uuid7(), price=19, items_in_stock=10),
        Offer(id=uuid7(), price=29, items_in_stock=5),
    ]

    console_print_mock = mocker.patch("rich.console.Console.print")

    print_offers_table(offers)

    console_print_mock.assert_called_once()
    table_arg = console_print_mock.call_args[0][0]
    assert table_arg.row_count == len(offers)
