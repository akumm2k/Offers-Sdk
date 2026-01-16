import asyncio
from http import HTTPStatus
from typing import Dict
from urllib.parse import urljoin

import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from offers_sdk_applifting.http.auth_token.auth_token_manager import (
    AuthTokenManager,
)
from offers_sdk_applifting.http.base_client import (
    BaseHttpClient,
    HttpResponse,
)


class RequestsClient(BaseHttpClient):
    _ADAPTER: HTTPAdapter = HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[
                HTTPStatus.TOO_MANY_REQUESTS,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                HTTPStatus.BAD_GATEWAY,
                HTTPStatus.SERVICE_UNAVAILABLE,
                HTTPStatus.GATEWAY_TIMEOUT,
            ],
            allowed_methods=["GET", "POST"],
        )
    )

    @staticmethod
    def redact_auth_token_hook[**P](
        resp: requests.Response, *args: P.args, **kwargs: P.kwargs
    ) -> None:
        headers_to_redact = {
            BaseHttpClient._ACCESS_TOKEN_HEADER_KEY,
            BaseHttpClient._REFRESH_TOKEN_HEADER_KEY,
        }
        for header in headers_to_redact:
            if header in resp.request.headers:
                resp.request.headers[header] = "REDACTED"

    def filter_out_auth_response(
        self, resp: requests.Response
    ) -> bool:
        return not resp.url.endswith(self._auth_endpoint)

    def __init__(
        self,
        *,
        base_url: str,
        refresh_token: str,
        auth_endpoint: str,
        token_manager: AuthTokenManager,
        backend: str = "filesystem",
    ) -> None:
        super().__init__(
            base_url=base_url,
            refresh_token=refresh_token,
            auth_endpoint=auth_endpoint,
            token_manager=token_manager,
        )
        self._session = requests_cache.CachedSession(
            cache_name=BaseHttpClient._CACHE_PATH / "requests_cache",
            backend=backend,
            cache_control=True,
            expire_after=60 * 5,
            ignored_params=[
                BaseHttpClient._ACCESS_TOKEN_HEADER_KEY,
                BaseHttpClient._REFRESH_TOKEN_HEADER_KEY,
            ],
            allowable_methods=["GET"],
            serializer="json",
            filter_fn=self.filter_out_auth_response,
        )
        self._session.mount("https://", RequestsClient._ADAPTER)

    async def _unauthenticated_get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        await self._ensure_refresh_token()

        def sync_get():
            url = urljoin(self._base_url, endpoint)
            response = self._session.get(
                url,
                params=params,
                headers=headers | self._default_headers,
                hooks={
                    "response": RequestsClient.redact_auth_token_hook
                },
            )
            return HttpResponse(
                status_code=HTTPStatus(response.status_code),
                json=response.json(),
                from_cache=response.from_cache,
            )

        return await asyncio.to_thread(sync_get)

    async def _unauthenticated_post(
        self, endpoint: str, data: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        def sync_post():
            url = urljoin(self._base_url, endpoint)
            response = self._session.post(
                url,
                json=data,
                headers=headers | self._default_headers,
            )
            return HttpResponse(
                status_code=HTTPStatus(response.status_code),
                json=response.json(),
                from_cache=response.from_cache,
            )

        return await asyncio.to_thread(sync_post)
