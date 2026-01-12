import os
from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    auth_endpoint: str
    refresh_token: str

    BASE_URL_ENV_KEY = "OFFERS_API_BASE_URL"
    AUTH_ENDPOINT_ENV_KEY = "AUTH_ENDPOINT"
    REFRESH_TOKEN_ENV_KEY = "REFRESH_TOKEN"

    @classmethod
    def from_env(cls: Type[ApiConfig]) -> ApiConfig:
        try:
            return cls(
                base_url=os.environ[ApiConfig.BASE_URL_ENV_KEY],
                auth_endpoint=os.environ[
                    ApiConfig.AUTH_ENDPOINT_ENV_KEY
                ],
                refresh_token=os.environ[
                    ApiConfig.REFRESH_TOKEN_ENV_KEY
                ],
            )
        except KeyError as e:
            missing_var = e.args[0]
            raise EnvironmentError(
                f"Unset environment variable: {missing_var}"
            ) from e
