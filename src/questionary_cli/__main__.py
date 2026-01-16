import logging
from pathlib import Path

from dotenv import load_dotenv

from offers_sdk_applifting.config import ApiConfig
from questionary_cli.app import run_cli
from questionary_cli.container import Container


def setup_logging() -> None:
    package_dir = Path(__file__).parent
    log_dir = package_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "offers_cli.log"

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=str(log_file),
        filemode="a",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )


def main() -> None:
    setup_logging()
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
    container.config.persistent_auth_token_key.from_env(
        ApiConfig.PERSISTENT_AUTH_TOKEN_KEY, required=True
    )

    run_cli()


if __name__ == "__main__":
    main()
    main()
