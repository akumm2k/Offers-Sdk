import logging

from dotenv import load_dotenv

from container import Container
from offers_cli.app import run_cli
from offers_sdk.config import ApiConfig

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="offers_sdk.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    load_dotenv()
    container = Container()
    container.wire(modules=[__name__])
    container.config.base_url.from_env(
        ApiConfig.BASE_URL_ENV_KEY, required=True
    )
    container.config.auth_endpoint.from_env(
        ApiConfig.AUTH_ENDPOINT_ENV_KEY, required=True
    )
    container.config.refresh_token.from_env(
        ApiConfig.REFRESH_TOKEN_ENV_KEY, required=True
    )

    run_cli()
