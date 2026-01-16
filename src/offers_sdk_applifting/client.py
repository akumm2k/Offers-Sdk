import uuid
from http import HTTPStatus
from typing import Awaitable, Callable, List, Optional
from uuid import UUID

from offers_sdk_applifting.config import ApiConfig
from offers_sdk_applifting.exceptions import (
    AuthenticationError,
    SDKError,
    ServerError,
    ValidationError,
)
from offers_sdk_applifting.http.auth_token.keyring_token_manager import (
    KeyringTokenManager,
)
from offers_sdk_applifting.http.base_client import (
    BaseHttpClient,
    HttpResponse,
    TokenRefreshError,
)
from offers_sdk_applifting.http.requests_client import RequestsClient
from offers_sdk_applifting.models import (
    Offer,
    Offers,
    Product,
    ProductID,
)

TOKEN_ERROR_MESSAGES = {
    HTTPStatus.UNAUTHORIZED: "Failed to refresh token",
    HTTPStatus.BAD_REQUEST: "Bad authentication: Check refresh token",
    HTTPStatus.UNPROCESSABLE_CONTENT: "Malformed authentication request",
}


def handle_token_refresh_error[**P, T](
    decorated_func: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await decorated_func(*args, **kwargs)
        except TokenRefreshError as exc:
            message = TOKEN_ERROR_MESSAGES.get(
                exc.http_response.status_code,
                "Unknown token refresh error",
            )
            raise AuthenticationError(
                message, exc.http_response
            ) from exc

    return wrapper


class OffersClient:
    def __init__(
        self,
        api_config: ApiConfig,
        http_client: Optional[BaseHttpClient] = None,
    ) -> None:
        self._http_client = http_client or RequestsClient(
            base_url=api_config.base_url,
            refresh_token=api_config.refresh_token,
            auth_endpoint=api_config.auth_endpoint,
            token_manager=KeyringTokenManager(
                token_key=api_config.persistent_auth_token_key
            ),
        )
        self._api_config = api_config

    @staticmethod
    def _validate_response(resp: HttpResponse) -> None:
        match resp.status_code:
            case HTTPStatus.UNAUTHORIZED:
                raise AuthenticationError("Check refresh token", resp)
            case HTTPStatus.UNPROCESSABLE_CONTENT:
                raise ValidationError(
                    "Malformed authentication request", resp
                )
            case code if code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                raise ServerError("Server error", resp)
            case code if not code.is_success:
                raise SDKError("Unexpected error", resp)

    @staticmethod
    def _validate_register_product_response(
        resp: HttpResponse, product_id: UUID
    ) -> None:
        match resp.status_code:
            case HTTPStatus.CONFLICT:
                raise ValidationError(
                    f"Product with ID {product_id} already exists",
                    resp,
                )
        OffersClient._validate_response(resp)

    @handle_token_refresh_error
    async def get_offers(self, product_id: UUID) -> List[Offer]:
        resp = await self._http_client.get(
            f"products/{product_id}/offers"
        )
        OffersClient._validate_response(resp)
        offers: List[Offer] = Offers.validate_python(
            resp.get_json_as(list)
        )
        return offers

    @handle_token_refresh_error
    async def register_product(
        self, product: Product, product_id: Optional[UUID] = None
    ) -> ProductID:
        product_id = product_id or uuid.uuid7()
        id_payload = {"id": str(product_id)}
        response = await self._http_client.post(
            "products/register",
            data=product.model_dump() | id_payload,
        )
        OffersClient._validate_register_product_response(
            response, product_id
        )
        data = response.get_json_as(dict)
        return ProductID(**data)
