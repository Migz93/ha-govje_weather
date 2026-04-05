"""
API Client for govje_weather.

Fetches weather forecast data from the Government of Jersey public API.
No authentication is required — the endpoint is a public Azure Blob Storage URL.

Exception hierarchy:
    GOVJEWeatherApiClientError (base)
    └── GOVJEWeatherApiClientCommunicationError (network/timeout/HTTP error)
"""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp

from custom_components.govje_weather.const import REMOTE_URL


class GOVJEWeatherApiClientError(Exception):
    """Base exception for GOV.JE Weather API errors."""


class GOVJEWeatherApiClientCommunicationError(GOVJEWeatherApiClientError):
    """Exception for communication errors (network, timeout, HTTP error)."""


class GOVJEWeatherApiClient:
    """
    API client for the GOV.JE weather forecast service.

    Fetches JSON forecast data from the Government of Jersey's public
    Azure Blob Storage endpoint. No credentials are required.

    Attributes:
        _session: The aiohttp ClientSession for making requests.
    """

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """
        Initialize the API client.

        Args:
            session: The aiohttp ClientSession to use for requests.
        """
        self._session = session

    async def async_get_data(self) -> Any:
        """
        Fetch the latest Jersey weather forecast from the GOV.JE API.

        Returns:
            A dictionary containing the full forecast JSON.

        Raises:
            GOVJEWeatherApiClientCommunicationError: If a network, timeout,
                or HTTP error occurs.
            GOVJEWeatherApiClientError: For any other unexpected error.
        """
        return await self._api_wrapper(method="get", url=REMOTE_URL)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
    ) -> Any:
        """
        Wrapper for API requests with unified error handling.

        Args:
            method: The HTTP method (e.g. "get").
            url: The URL to request.
            headers: Optional extra headers.

        Returns:
            The parsed JSON response.

        Raises:
            GOVJEWeatherApiClientCommunicationError: On timeout or network error.
            GOVJEWeatherApiClientError: On any other unexpected error.
        """
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                )
                response.raise_for_status()
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout fetching GOV.JE weather data - {exception}"
            raise GOVJEWeatherApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching GOV.JE weather data - {exception}"
            raise GOVJEWeatherApiClientCommunicationError(msg) from exception
        except Exception as exception:
            msg = f"Unexpected error fetching GOV.JE weather data - {exception}"
            raise GOVJEWeatherApiClientError(msg) from exception
