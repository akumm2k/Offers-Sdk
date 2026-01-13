from dependency_injector import containers, providers

from offers_sdk.client import OffersClient
from offers_sdk.config import ApiConfig
from offers_sdk.http.base_client import BaseHttpClient
from offers_sdk.http.requests_client import RequestsClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    http_client: providers.Singleton[BaseHttpClient] = (
        providers.Singleton(
            RequestsClient,
            base_url=config.base_url,
            refresh_token=config.refresh_token,
            auth_endpoint=config.auth_endpoint,
            persistent_auth_token_key=config.persistent_auth_token_key,  # noqa: E501
        )
    )
    api_config: providers.Singleton[ApiConfig] = providers.Singleton(
        ApiConfig,
        base_url=config.base_url,
        auth_endpoint=config.auth_endpoint,
        refresh_token=config.refresh_token,
        persistent_auth_token_key=config.persistent_auth_token_key,
    )
    offers_client: providers.Factory[OffersClient] = (
        providers.Factory(
            OffersClient,
            http_client=http_client,
            api_config=api_config,
        )
    )
