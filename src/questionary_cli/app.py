import asyncio
import logging

import questionary
from dependency_injector.wiring import Provide, inject

from container import Container
from offers_sdk.client import OffersClient
from questionary_cli.actions import Actions
from questionary_cli.commands.get_offers import run as get_offers
from questionary_cli.commands.register_product import (
    run as register_product,
)

LOGGER = logging.getLogger(__name__)


@inject
def run_cli(
    client: OffersClient = Provide[Container.offers_client],
) -> None:
    LOGGER.info("Starting Offers CLI")
    while True:
        try:
            if run_is_finished(client):
                break
        except Exception as e:
            questionary.print(
                f"❌ An error occurred: {e}", style="bold fg:red"
            )
            LOGGER.error(
                "An error occurred in the CLI", exc_info=True
            )


def run_is_finished(client: OffersClient) -> bool:
    action = questionary.select(
        "Choose an action:",
        choices=[
            Actions.REGISTER_PRODUCT,
            Actions.GET_OFFERS,
            Actions.EXIT,
        ],
    ).ask()

    if action == Actions.REGISTER_PRODUCT:
        asyncio.run(register_product(client))
    elif action == Actions.GET_OFFERS:
        asyncio.run(get_offers(client))
    elif action == Actions.EXIT:
        questionary.print("Bye!")
        return True

    return False
