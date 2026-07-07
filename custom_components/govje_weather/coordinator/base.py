"""
Core DataUpdateCoordinator for govje_weather.

Manages periodic fetching of weather forecast data from the GOV.JE API
and distributes updates to all entities.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from custom_components.govje_weather.api import GOVJEWeatherApiClientCommunicationError, GOVJEWeatherApiClientError
from custom_components.govje_weather.const import LOGGER
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.govje_weather.data import GOVJEWeatherConfigEntry

RETRY_DELAY = 30
RETRY_TIMEOUT = 30


class GOVJEWeatherDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """
    Coordinator that fetches GOV.JE weather forecast data on a schedule.

    All entities receive the same raw JSON dict from the API. Time-of-day
    processing is done per-entity at read time using helpers in
    coordinator/data_processing.py.
    """

    config_entry: GOVJEWeatherConfigEntry

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch the latest forecast from the GOV.JE API.

        Returns:
            The parsed JSON forecast as a dictionary.

        Raises:
            UpdateFailed: If the API request fails for any reason.
        """
        try:
            data: dict[str, Any] = await self.config_entry.runtime_data.client.async_get_data()
        except GOVJEWeatherApiClientCommunicationError as exception:
            return await self._async_retry_or_use_cached_data(exception)
        except GOVJEWeatherApiClientError as exception:
            LOGGER.exception("Unexpected error fetching GOV.JE weather")
            return self._cached_data_or_raise(exception)
        return data

    async def _async_retry_or_use_cached_data(
        self,
        exception: GOVJEWeatherApiClientCommunicationError,
    ) -> dict[str, Any]:
        """Retry a transient communication failure, then fall back to cached data."""
        LOGGER.warning(
            "Communication error fetching GOV.JE weather, retrying in %d seconds - %s",
            RETRY_DELAY,
            exception,
        )
        await asyncio.sleep(RETRY_DELAY)

        try:
            data: dict[str, Any] = await self.config_entry.runtime_data.client.async_get_data(timeout=RETRY_TIMEOUT)
        except GOVJEWeatherApiClientCommunicationError as retry_exception:
            LOGGER.warning(
                "Retry fetching GOV.JE weather failed, using cached data if available - %s",
                retry_exception,
            )
            return self._cached_data_or_raise(retry_exception)
        except GOVJEWeatherApiClientError as retry_exception:
            LOGGER.exception("Unexpected error retrying GOV.JE weather fetch")
            return self._cached_data_or_raise(retry_exception)

        LOGGER.info("Retry fetching GOV.JE weather succeeded")
        return data

    def _cached_data_or_raise(self, exception: GOVJEWeatherApiClientError) -> dict[str, Any]:
        """Return cached coordinator data, or raise UpdateFailed when no cache exists."""
        if self.data:
            LOGGER.warning("Using cached GOV.JE weather data after update failure")
            return self.data

        raise UpdateFailed(
            translation_domain="govje_weather",
            translation_key="update_failed",
            retry_after=RETRY_DELAY,
        ) from exception
