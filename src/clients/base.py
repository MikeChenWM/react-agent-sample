"""Base API client class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class BaseAPIClient(ABC):
    """Base class for all API clients."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 30.0):
        """Initialize API client with key, base URL and timeout."""
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout, headers=self._get_default_headers()
            )
        return self._client

    @abstractmethod
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        """Make HTTP request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = await self.client.request(
                method=method, url=url, params=params, json=json_data
            )

            response_data = response.json() if response.content else {}

            return APIResponse(
                success=response.is_success,
                data=response_data,
                status_code=response.status_code,
                error=None
                if response.is_success
                else response_data.get("message", "API request failed"),
            )

        except httpx.RequestError as e:
            return APIResponse(
                success=False, error=f"Request failed: {str(e)}", status_code=None
            )
        except Exception as e:
            return APIResponse(
                success=False, error=f"Unexpected error: {str(e)}", status_code=None
            )

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
