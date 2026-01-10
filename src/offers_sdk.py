from http_client.http_client import (
    HttpClient,
    HttpResponse,
    TokenRefreshError,
)
import uuid
from exceptions import (
    AuthenticationError,
    ValidationError,
    ServerError,
)
from uuid import UUID
from models import Product, Offers, ProductID, Offer
from http import HTTPStatus
from typing import List, Dict, Callable, Coroutine, Optional

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
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    @staticmethod
    def _validate_response(resp: HttpResponse) -> Dict:
        match resp.status_code:
            case HTTPStatus.UNAUTHORIZED:
                raise AuthenticationError("Check refresh token")
            case HTTPStatus.UNPROCESSABLE_CONTENT:
                raise ValidationError()
            case code if code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                raise ServerError()
        return resp.json

    @staticmethod
    def _validate_register_product_response(
        resp: HttpResponse, product_id: UUID
    ) -> Dict:
        match resp.status_code:
            case HTTPStatus.CONFLICT:
                raise ValidationError(
                    f"Product with ID {product_id} already exists"
                )
        return resp.json

    @handle_token_refresh_error
    async def get_offers(self, product_id: UUID) -> List[Offer]:
        resp = await self._http_client.get(f"{product_id}/offers")
        data = OffersSDK._validate_response(resp)
        return Offers.validate_python(data)

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
        data = OffersSDK._validate_register_product_response(
            response, product_id
        )

        return ProductID(**data)
