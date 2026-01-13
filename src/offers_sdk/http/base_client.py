import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import (
    Dict,
    Optional,
)

import jwt
import keyring

from offers_sdk.http.http_response import HttpResponse

LOGGER = logging.getLogger(__name__)


class TokenRefreshError(Exception):
    def __init__(
        self, message: str, http_response: HttpResponse
    ) -> None:
        super().__init__(message)
        self.http_response = http_response


class BaseHttpClient(ABC):
    _KEYRING_SERVICE_NAME = "offers_sdk"

    def __init__(
        self,
        *,
        base_url: str,
        refresh_token: str,
        auth_endpoint: str,
        persistent_auth_token_key: str,
    ) -> None:
        self._base_url = base_url
        self._refresh_token = refresh_token
        self._auth_endpoint = auth_endpoint
        self._access_token: Optional[str] = None
        self._token_expiry: datetime = datetime.min.replace(
            tzinfo=timezone.utc
        )
        self._default_headers: Dict[str, str] = {}
        self._persistent_auth_token_key = persistent_auth_token_key
        self._load_auth_token_from_keyring()

    def _load_auth_token_from_keyring(self) -> None:
        LOGGER.debug("Loading auth token from keyring")
        if self._persistent_auth_token_key:
            token = keyring.get_password(
                BaseHttpClient._KEYRING_SERVICE_NAME,
                self._persistent_auth_token_key,
            )
            if token:
                token_expiry = self._decode_jwt_expiry(token)
                if datetime.now(timezone.utc) < token_expiry:
                    self._update_auth_token(token, token_expiry)
                    LOGGER.debug("Loaded auth token from keyring")

    def _update_auth_token(
        self, token: str, token_expiry: datetime
    ) -> None:
        self._access_token = token
        self._token_expiry = token_expiry
        self._default_headers["Bearer"] = token

    def _save_auth_token_to_keyring(self, token: str) -> None:
        LOGGER.debug("Saving auth token to keyring")
        if self._persistent_auth_token_key and token:
            keyring.set_password(
                BaseHttpClient._KEYRING_SERVICE_NAME,
                self._persistent_auth_token_key,
                token,
            )
            LOGGER.debug("Saved auth token to keyring")

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
            token_expiry = self._decode_jwt_expiry(token)
            self._update_auth_token(token, token_expiry)
            self._save_auth_token_to_keyring(token)
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
