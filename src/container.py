from dependency_injector import containers, providers
from http_client.http_client import HttpClient
from http_client.requests_client import RequestsClient
from offers_sdk import OffersSDK


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    http_client: providers.Singleton[HttpClient] = (
        providers.Singleton(
            RequestsClient,
            base_url=config.base_url,
            refresh_token=config.refresh_token,
            auth_endpoint=config.auth_endpoint,
        )
    )
    offers_sdk: providers.Factory[OffersSDK] = providers.Factory(
        OffersSDK,
        http_client=http_client,
        base_url=config.base_url,
    )
