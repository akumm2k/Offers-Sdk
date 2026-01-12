from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import wraps
from http import HTTPStatus
from types import CoroutineType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)

import jwt


class TokenRefreshError(Exception):
    def __init__(
        self, message: str, http_response: HttpResponse
    ) -> None:
        super().__init__(message)
        self.http_response = http_response


def ensure_refresh_token(
    http_call: Callable[..., CoroutineType[Any, Any, HttpResponse]],
) -> Callable[..., CoroutineType[Any, Any, HttpResponse]]:
    @wraps(http_call)
    async def wrapper(
        self: HttpClient,
        *args: Tuple[Any, ...],
        **kwargs: Dict[str, Any],
    ) -> HttpResponse:
        await self._ensure_refresh_token()
        return await http_call(self, *args, **kwargs)

    return wrapper


class HttpResponse:
    def __init__(
        self,
        status_code: HTTPStatus,
        json: Dict | List,
    ):
        self.status_code = status_code
        self.json = json

    def get_json_as[T](self, type: Type[T]) -> T:
        if isinstance(self.json, type):
            return self.json
        raise ValueError("Response JSON is not a dictionary")


class HttpClient(ABC):
    def __init__(
        self, *, base_url: str, refresh_token: str, auth_endpoint: str
    ) -> None:
        self._base_url = base_url
        self._refresh_token = refresh_token
        self._auth_endpoint = auth_endpoint
        self._access_token: Optional[str] = None
        self._token_expiry: datetime = datetime.min.replace(
            tzinfo=timezone.utc
        )
        self._default_headers: Dict[str, str] = {}

    async def _ensure_refresh_token(self) -> None:
        if (
            self._access_token is None
            or self._token_expiry is None
            or datetime.now(timezone.utc) >= self._token_expiry
        ):
            await self._refresh_access_token()

    async def _refresh_access_token(self) -> None:
        resp = await self._unauthenticated_post(
            self._auth_endpoint,
            headers={"Bearer": self._refresh_token},
        )

        if resp.status_code == HTTPStatus.OK:
            data = resp.get_json_as(dict)
            token = data["access_token"]
            self._access_token = token
            self._token_expiry = self._decode_jwt_expiry(token)
            self._default_headers["Bearer"] = token
        else:
            raise TokenRefreshError(
                "Failed to refresh access token", resp
            )

    def _decode_jwt_expiry(self, token: str) -> datetime:
        payload = jwt.decode(
            token, options={"verify_signature": False}
        )
        ret = datetime.fromtimestamp(
            payload["expires"], tz=timezone.utc
        )
        return ret

    @abstractmethod
    async def get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass  # pragma: no cover

    @abstractmethod
    async def post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass  # pragma: no cover

    @abstractmethod
    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass  # pragma: no cover
