import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HAClient:
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/') + '/'
        if not token:
            raise ValueError("HA_TOKEN is missing.")
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-loaded httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                transport=httpx.AsyncHTTPTransport(retries=3),
                timeout=httpx.Timeout(15.0)
            )
        return self._client

    async def get(self, endpoint: str, params=None):
        response = await self.client.get(endpoint.lstrip('/'), params=params)
        response.raise_for_status()
        return response

    async def post(self, endpoint: str, json_data=None):
        response = await self.client.post(endpoint.lstrip('/'), json=json_data)
        response.raise_for_status()
        return response
    
    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()