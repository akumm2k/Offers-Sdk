from typing import Optional

import keyring

from offers_sdk.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)


class KeyringTokenManager(AuthTokenManager):
    _KEYRING_SERVICE_NAME = "offers_sdk"

    def __init__(self, token_key: str) -> None:
        self._token_key = token_key
        super().__init__()

    def get_token(self) -> Optional[str]:
        token = keyring.get_password(
            KeyringTokenManager._KEYRING_SERVICE_NAME, self._token_key
        )
        return token

    def store_token(self, token: str) -> None:
        keyring.set_password(
            KeyringTokenManager._KEYRING_SERVICE_NAME,
            self._token_key,
            token,
        )
