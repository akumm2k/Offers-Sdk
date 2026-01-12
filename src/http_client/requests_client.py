import asyncio
from http import HTTPStatus
from typing import Dict
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from http_client.http_client import (
    HttpClient,
    HttpResponse,
    ensure_refresh_token,
)


class RequestsClient(HttpClient):
    def __init__(
        self, base_url: str, refresh_token: str, auth_endpoint: str
    ) -> None:
        super().__init__(
            refresh_token=refresh_token, auth_endpoint=auth_endpoint
        )
        self._base_url = base_url
        adapter = HTTPAdapter(
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
        self._session = requests.Session()
        self._session.mount("https://", adapter)

    @ensure_refresh_token
    async def get(
        self, endpoint: str, params: Dict = {}, headers: Dict = {}
    ) -> HttpResponse:
        def sync_get():
            url = urljoin(self._base_url, endpoint)
            response = self._session.get(
                url,
                params=params,
                headers=headers | self._default_headers,
            )
            return HttpResponse(
                status_code=HTTPStatus(response.status_code),
                json=response.json(),
            )

        return await asyncio.to_thread(sync_get)

    @ensure_refresh_token
    async def post(
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
            )

        return await asyncio.to_thread(sync_post)
