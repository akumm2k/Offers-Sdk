import os
from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    auth_endpoint: str
    refresh_token: str

    @classmethod
    def from_env(cls: Type[ApiConfig]) -> ApiConfig:
        try:
            return cls(
                base_url=os.environ["OFFERS_API_BASE_URL"],
                auth_endpoint=os.environ["AUTH_ENDPOINT"],
                refresh_token=os.environ["REFRESH_TOKEN"],
            )
        except KeyError as e:
            missing_var = e.args[0]
            raise EnvironmentError(
                f"Unset environment variable: {missing_var}"
            ) from e
