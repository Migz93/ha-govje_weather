"""Sensor platform for govje_weather."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.govje_weather.const import PARALLEL_UPDATES as PARALLEL_UPDATES

from .weather_sensors import SENSOR_DESCRIPTIONS, GOVJEWeatherSensor

if TYPE_CHECKING:
    from custom_components.govje_weather.data import GOVJEWeatherConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GOV.JE Weather sensor entities."""
    async_add_entities(
        GOVJEWeatherSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=description,
        )
        for description in SENSOR_DESCRIPTIONS
    )
