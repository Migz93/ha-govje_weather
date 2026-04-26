"""
GOV.JE Weather integration for Home Assistant.

Provides weather data for Jersey (Channel Islands) from the Government of
Jersey's public weather service API.

Data source:
    https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json

For more details:
    https://github.com/Migz93/ha-govje_weather
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .api import GOVJEWeatherApiClient
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER
from .coordinator import GOVJEWeatherDataUpdateCoordinator
from .data import GOVJEWeatherData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import GOVJEWeatherConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.WEATHER,
]

# This integration is configured via config entries only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
) -> bool:
    """
    Set up the GOV.JE Weather integration from a config entry.

    Creates the API client and coordinator, performs the first data fetch,
    and forwards setup to the sensor and weather platforms.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being set up.

    Returns:
        True if setup was successful.
    """
    client = GOVJEWeatherApiClient(session=async_get_clientsession(hass))

    scan_interval_minutes = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = GOVJEWeatherDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(minutes=scan_interval_minutes),
        always_update=False,
    )

    entry.runtime_data = GOVJEWeatherData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being unloaded.

    Returns:
        True if unload was successful.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
) -> None:
    """
    Reload a config entry when options change.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry being reloaded.
    """
    await hass.config_entries.async_reload(entry.entry_id)
