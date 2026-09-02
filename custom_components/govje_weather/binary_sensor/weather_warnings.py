"""Weather warning binary sensor entities for GOV.JE Weather."""

from __future__ import annotations

from typing import Any

from custom_components.govje_weather.coordinator import GOVJEWeatherDataUpdateCoordinator
from custom_components.govje_weather.entity.base import GOVJEWeatherEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription


class GOVJEWeatherWarningBinarySensor(GOVJEWeatherEntity, BinarySensorEntity):
    """Represent a weather warning supplied by the Government of Jersey."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: GOVJEWeatherDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialise the weather warning binary sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)

    @property
    def is_on(self) -> bool | None:
        """Return whether this warning is active."""
        warnings = self.coordinator.data.get("warnings") if self.coordinator.data else None
        if not warnings:
            return None
        return bool(warnings.get(self.entity_description.key))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the raw warning payload and publication metadata."""
        warnings = self.coordinator.data.get("warnings") if self.coordinator.data else None
        if not warnings:
            return None

        attributes: dict[str, Any] = {"last_checked": warnings.get("lastChecked")}
        data_key = f"{self.entity_description.key}Data"
        if data_key in warnings:
            attributes["warning_data"] = warnings[data_key]
        if self.entity_description.key == "TideWarning" and "TideWarningImageURL" in warnings:
            attributes["warning_image_url"] = warnings["TideWarningImageURL"]
        return attributes


WARNING_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(key="TideWarning", translation_key="tide_warning", icon="mdi:waves-arrow-up"),
    BinarySensorEntityDescription(
        key="ThunderWarning", translation_key="thunder_warning", icon="mdi:weather-lightning"
    ),
    BinarySensorEntityDescription(
        key="ThunderstormWarningALD",
        translation_key="thunderstorm_warning_ald",
        icon="mdi:weather-lightning-rainy",
    ),
    BinarySensorEntityDescription(key="WindWarning", translation_key="wind_warning", icon="mdi:weather-windy"),
    BinarySensorEntityDescription(key="SnowWarning", translation_key="snow_warning", icon="mdi:weather-snowy"),
    BinarySensorEntityDescription(key="SnowAlert", translation_key="snow_alert", icon="mdi:weather-snowy-heavy"),
    BinarySensorEntityDescription(key="IceWarning", translation_key="ice_warning", icon="mdi:weather-snowy-rainy"),
)
