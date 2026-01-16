from typing import List
from uuid import UUID

import questionary
from rich import table
from rich.console import Console

from offers_sdk_applifting.client import OffersClient
from offers_sdk_applifting.models import Offer

CONSOLE = Console()


def print_offers_table(offers: List[Offer]) -> None:
    offers_table = table.Table(
        "Offer ID",
        "Price",
        "Items in Stock",
        title="Offers",
        show_lines=True,
        header_style="bold magenta",
    )

    for offer in offers:
        offers_table.add_row(
            str(offer.id),
            f"{offer.price}",
            f"{offer.items_in_stock}",
        )
    CONSOLE.print(offers_table)


async def run(client: OffersClient) -> None:
    product_id_str = await questionary.text(
        "Product ID: "
    ).ask_async()
    product_id = UUID(product_id_str)

    offers = await client.get_offers(product_id)
    if not offers:
        questionary.print("No offers found for this product.")
        return

    print_offers_table(offers)
