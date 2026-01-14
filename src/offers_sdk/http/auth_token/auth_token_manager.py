from abc import ABC, abstractmethod
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

import jwt


class AuthTokenManager(ABC):
    def __init__(self) -> None:
        super().__init__()
        token = self.get_token()
        if token and self._is_string_valid_token(token):
            self.update_auth_token(token)
        else:
            self._access_token: Optional[str] = None
            self._token_expiry: datetime = datetime.min.replace(
                tzinfo=timezone.utc
            )

    def update_auth_token(
        self, valid_token: str, save: bool = False
    ) -> None:
        self._access_token = valid_token
        self._token_expiry = self._decode_jwt_expiry(valid_token)
        if save:
            self.store_token(valid_token)

    def is_current_token_expired(self) -> bool:
        return (
            self._access_token is None
            or self._token_expiry <= datetime.now(timezone.utc)
        )

    @abstractmethod
    def get_token(self) -> Optional[str]:
        pass

    @abstractmethod
    def store_token(self, token: str) -> None:
        pass

    @lru_cache
    def _decode_jwt_expiry(self, valid_token: str) -> datetime:
        payload = jwt.decode(
            valid_token, options={"verify_signature": False}
        )
        ret = datetime.fromtimestamp(
            payload["expires"], tz=timezone.utc
        )
        return ret

    def _is_string_valid_token(self, value: str) -> bool:
        try:
            expiry = self._decode_jwt_expiry(value)
            return datetime.now(timezone.utc) < expiry
        except jwt.DecodeError:
            return False
