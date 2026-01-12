import uuid
from http import HTTPStatus
from typing import Callable, Coroutine, List, Optional
from uuid import UUID

from config import ApiConfig
from exceptions import (
    AuthenticationError,
    ServerError,
    ValidationError,
)
from http_client.http_client import (
    HttpClient,
    HttpResponse,
    TokenRefreshError,
)
from http_client.requests_client import RequestsClient
from models import Offer, Offers, Product, ProductID

TOKEN_ERROR_MESSAGES = {
    HTTPStatus.UNAUTHORIZED: "Failed to refresh token",
    HTTPStatus.BAD_REQUEST: "Bad authentication: Check refresh token",
    HTTPStatus.UNPROCESSABLE_CONTENT: "Malformed authentication request",
}


def handle_token_refresh_error(
    decorated_func: Callable[..., Coroutine],
) -> Callable[..., Coroutine]:
    async def wrapper[**P](*args: P.args, **kwargs: P.kwargs):
        try:
            return await decorated_func(*args, **kwargs)
        except TokenRefreshError as exc:
            message = TOKEN_ERROR_MESSAGES.get(
                exc.http_response.status_code,
                "Unknown token refresh error",
            )
            raise AuthenticationError(message) from exc

    return wrapper


class OffersSDK:
    def __init__(
        self,
        api_config: ApiConfig,
        http_client: Optional[HttpClient] = None,
    ) -> None:
        self._http_client = http_client or RequestsClient(
            base_url=api_config.base_url,
            refresh_token=api_config.refresh_token,
            auth_endpoint=api_config.auth_endpoint,
        )
        self._api_config = api_config

    @staticmethod
    def _validate_response(resp: HttpResponse) -> None:
        match resp.status_code:
            case HTTPStatus.UNAUTHORIZED:
                raise AuthenticationError("Check refresh token")
            case HTTPStatus.UNPROCESSABLE_CONTENT:
                raise ValidationError(
                    f"\nServer Response: {resp.json}"
                )
            case code if code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                raise ServerError()

    @staticmethod
    def _validate_register_product_response(
        resp: HttpResponse, product_id: UUID
    ) -> None:
        OffersSDK._validate_response(resp)
        match resp.status_code:
            case HTTPStatus.CONFLICT:
                raise ValidationError(
                    f"Product with ID {product_id} already exists"
                    f"\nServer Response: {resp.json}"
                )

    @handle_token_refresh_error
    async def get_offers(self, product_id: UUID) -> List[Offer]:
        resp = await self._http_client.get(f"{product_id}/offers")
        OffersSDK._validate_response(resp)
        return Offers.validate_python(resp.get_json_as(list))

    @handle_token_refresh_error
    async def register_product(
        self, product: Product, product_id: Optional[UUID] = None
    ) -> ProductID:
        product_id = product_id or uuid.uuid7()
        id_payload = {"id": str(product_id)}
        response = await self._http_client.post(
            "products",
            data=product.model_dump() | id_payload,
        )
        OffersSDK._validate_register_product_response(
            response, product_id
        )
        data = response.get_json_as(dict)
        return ProductID(**data)
