"""
Base entity class for govje_weather.

All entities in this integration inherit from GOVJEWeatherEntity, which
provides common device info, unique ID generation, and coordinator wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.govje_weather.const import ATTRIBUTION
from custom_components.govje_weather.coordinator import GOVJEWeatherDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class GOVJEWeatherEntity(CoordinatorEntity[GOVJEWeatherDataUpdateCoordinator]):
    """
    Base entity class for govje_weather.

    All entities inherit from this class to get:
    - Automatic coordinator data updates
    - Shared device info (one device per config entry)
    - Unique ID generation keyed to the config entry + description key
    - Attribution
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GOVJEWeatherDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """
        Initialize the base entity.

        Args:
            coordinator: The data update coordinator.
            entity_description: The entity description for this entity.
        """
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name="GOV.JE Weather",
            manufacturer="Government of Jersey",
            model="Weather Forecast",
        )
