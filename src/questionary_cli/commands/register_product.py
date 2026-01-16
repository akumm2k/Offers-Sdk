import questionary

from offers_sdk_applifting.models import Product


async def run(client) -> None:
    name = await questionary.text("Product name:").ask_async()
    description = await questionary.text(
        "Product description:"
    ).ask_async()

    product = Product(name=name, description=description)

    try:
        product_id = await client.register_product(product)
    except Exception as e:
        questionary.print(
            f"❌ Failed to register product: {e}", style="bold fg:red"
        )
        return
    questionary.print(
        f"✅ Product registered with ID: {product_id.product_id}",
        style="bold fg:green",
    )
