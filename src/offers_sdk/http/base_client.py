from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import (
    Dict,
    Optional,
)

import jwt

from offers_sdk.http.http_response import HttpResponse


class TokenRefreshError(Exception):
    def __init__(
        self, message: str, http_response: HttpResponse
    ) -> None:
        super().__init__(message)
        self.http_response = http_response


class BaseHttpClient(ABC):
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

        if resp.status_code.is_success:
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

    async def get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        await self._ensure_refresh_token()
        return await self._unauthenticated_get(
            endpoint, params, headers
        )

    async def post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        await self._ensure_refresh_token()
        return await self._unauthenticated_post(
            endpoint, data, headers
        )

    @abstractmethod
    async def _unauthenticated_get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass  # pragma: no cover

    @abstractmethod
    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass  # pragma: no cover
