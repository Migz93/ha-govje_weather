"""
Core DataUpdateCoordinator for govje_weather.

Manages periodic fetching of weather forecast data from the GOV.JE API
and distributes updates to all entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.govje_weather.api import GOVJEWeatherApiClientCommunicationError, GOVJEWeatherApiClientError
from custom_components.govje_weather.const import LOGGER
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.govje_weather.data import GOVJEWeatherConfigEntry


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
            LOGGER.warning("Communication error fetching GOV.JE weather - %s", exception)
            raise UpdateFailed(
                translation_domain="govje_weather",
                translation_key="update_failed",
            ) from exception
        except GOVJEWeatherApiClientError as exception:
            LOGGER.exception("Unexpected error fetching GOV.JE weather")
            raise UpdateFailed(
                translation_domain="govje_weather",
                translation_key="update_failed",
            ) from exception
        return data
