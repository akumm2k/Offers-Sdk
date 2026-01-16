import logging
from abc import ABC, abstractmethod
from typing import (
    Dict,
)

from offers_sdk_applifting.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk_applifting.http.http_response import HttpResponse

LOGGER = logging.getLogger(__name__)


class TokenRefreshError(Exception):
    def __init__(
        self, message: str, http_response: HttpResponse
    ) -> None:
        super().__init__(message)
        self.http_response = http_response


class BaseHttpClient(ABC):
    _ACCESS_TOKEN_HEADER_KEY = "Bearer"
    _REFRESH_TOKEN_HEADER_KEY = "Bearer"

    def __init__(
        self,
        *,
        base_url: str,
        refresh_token: str,
        auth_endpoint: str,
        token_manager: AuthTokenManager,
    ) -> None:
        self._base_url = base_url
        self._refresh_token = refresh_token
        self._auth_endpoint = auth_endpoint
        self._default_headers: Dict[str, str] = {}
        self._token_manager = token_manager
        self._update_headers_with_token_on_load()

    def _update_headers_with_token_on_load(self) -> None:
        if not self._token_manager.is_current_token_expired():
            assert (
                token := self._token_manager.get_token()
            ) is not None
            self._default_headers[
                BaseHttpClient._ACCESS_TOKEN_HEADER_KEY
            ] = token

    def _update_auth_token(self, token: str) -> None:
        self._token_manager.update_auth_token(token, save=True)
        self._default_headers[
            BaseHttpClient._ACCESS_TOKEN_HEADER_KEY
        ] = token

    async def _ensure_refresh_token(self) -> None:
        if self._token_manager.is_current_token_expired():
            await self._refresh_access_token()

    async def _refresh_access_token(self) -> None:
        resp = await self._unauthenticated_post(
            self._auth_endpoint,
            headers={
                BaseHttpClient._REFRESH_TOKEN_HEADER_KEY: self._refresh_token
            },
        )

        if resp.status_code.is_success:
            data = resp.get_json_as(dict)
            token = data["access_token"]
            self._update_auth_token(token)
        else:
            raise TokenRefreshError(
                "Failed to refresh access token", resp
            )

    async def get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        LOGGER.debug(f"GET {endpoint} with params {params}")
        await self._ensure_refresh_token()
        resp = await self._unauthenticated_get(
            endpoint, params, headers
        )
        LOGGER.debug(f"Response: {resp}")
        return resp

    async def post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        LOGGER.debug(f"POST {endpoint} with data {data}")
        await self._ensure_refresh_token()
        resp = await self._unauthenticated_post(
            endpoint, data, headers
        )
        LOGGER.debug(f"Response: {resp}")
        return resp

    @abstractmethod
    async def _unauthenticated_get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass

    @abstractmethod
    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        pass
