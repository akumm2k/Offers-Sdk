from uuid import UUID

import questionary

from offers_sdk.client import OffersClient


async def run(client: OffersClient):
    product_id_str = await questionary.text(
        "Product ID: "
    ).ask_async()
    product_id = UUID(product_id_str)

    offers = await client.get_offers(product_id)
    if not offers:
        questionary.print("No offers found for this product.")
        return

    print(f"Offers for product {product_id}:")
    for offer in offers:
        questionary.print(
            f"{offer.id}: {offer.price}: {offer.items_in_stock}",
            style="bold fg:green bg:black underline",
        )
