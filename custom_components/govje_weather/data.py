"""
Custom types for govje_weather.

Defines the runtime data structure attached to each config entry.
Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import GOVJEWeatherApiClient
    from .coordinator import GOVJEWeatherDataUpdateCoordinator


type GOVJEWeatherConfigEntry = ConfigEntry[GOVJEWeatherData]


@dataclass
class GOVJEWeatherData:
    """Runtime data for govje_weather config entries.

    Stored as entry.runtime_data after successful setup.
    Provides typed access to the API client and coordinator instances.
    """

    client: GOVJEWeatherApiClient
    coordinator: GOVJEWeatherDataUpdateCoordinator
    integration: Integration
