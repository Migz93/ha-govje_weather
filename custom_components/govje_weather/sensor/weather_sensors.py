"""
Weather sensor entities for govje_weather.

Provides 14 sensor entities derived from the GOV.JE forecast API.
Time-of-day aware sensors automatically reflect the current period
(Morning / Afternoon / Evening) and expose future periods as attributes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from custom_components.govje_weather.coordinator import GOVJEWeatherDataUpdateCoordinator
from custom_components.govje_weather.coordinator.data_processing import (
    extract_temp_value,
    get_description_period,
    get_time_period,
    should_use_evening_data,
)
from custom_components.govje_weather.entity.base import GOVJEWeatherEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature


@dataclass(frozen=True, kw_only=True)
class GOVJEWeatherSensorEntityDescription(SensorEntityDescription):
    """Extended sensor entity description that includes a value function."""

    # time_aware=True means the sensor exposes per-period (Morning/Afternoon/Evening) attributes
    time_aware: bool = False
    # future_aware=True means the sensor exposes per-day attributes for future forecast days
    future_aware: bool = False


def _today(data: dict[str, Any]) -> dict[str, Any] | None:
    """Return today's (day 0) forecast dict, or None if unavailable."""
    days: list[dict[str, Any]] = data.get("forecastDay", [])
    return days[0] if days else None


def _period(data: dict[str, Any]) -> str:
    """Return the current period suffix: Morning, Afternoon, or Evening."""
    return get_time_period(data.get("forecastDate"))


def _desc_period(data: dict[str, Any]) -> str:
    """Return the current description prefix: morning, afternoon, or night."""
    return get_description_period(data.get("forecastDate"))


# ---------------------------------------------------------------------------
# Sensor descriptions (14 sensors)
# ---------------------------------------------------------------------------

SENSOR_DESCRIPTIONS: tuple[GOVJEWeatherSensorEntityDescription, ...] = (
    # --- Static (non-time-aware) sensors ---
    GOVJEWeatherSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        time_aware=False,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="uv_index",
        translation_key="uv_index",
        icon="mdi:weather-sunny-alert",
        state_class=SensorStateClass.MEASUREMENT,
        future_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="max_temp",
        translation_key="max_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        future_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="min_temp",
        translation_key="min_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        future_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="sunrise",
        translation_key="sunrise",
        icon="mdi:weather-sunset-up",
        future_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="sunset",
        translation_key="sunset",
        icon="mdi:weather-sunset-down",
        future_aware=True,
    ),
    # --- Time-aware sensors ---
    GOVJEWeatherSensorEntityDescription(
        key="wind_speed_mph",
        translation_key="wind_speed_mph",
        icon="mdi:weather-windy",
        native_unit_of_measurement="mph",
        state_class=SensorStateClass.MEASUREMENT,
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="wind_speed_knots",
        translation_key="wind_speed_knots",
        icon="mdi:windsock",
        native_unit_of_measurement="kn",
        state_class=SensorStateClass.MEASUREMENT,
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="wind_speed_kph",
        translation_key="wind_speed_kph",
        icon="mdi:speedometer",
        native_unit_of_measurement="km/h",
        state_class=SensorStateClass.MEASUREMENT,
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        icon="mdi:compass",
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="wind_force",
        translation_key="wind_force",
        icon="mdi:weather-windy",
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="rain_probability",
        translation_key="rain_probability",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="forecast_summary",
        translation_key="forecast_summary",
        icon="mdi:text-box-outline",
        time_aware=True,
    ),
    GOVJEWeatherSensorEntityDescription(
        key="confidence",
        translation_key="confidence",
        icon="mdi:check-circle-outline",
        time_aware=True,
    ),
)


def _get_native_value(key: str, data: dict[str, Any]) -> Any:
    """Return the native sensor value for the given key."""
    today = _today(data)
    if today is None:
        return None

    if key == "temperature":
        return extract_temp_value(data.get("currentTemprature"))

    if key == "uv_index":
        return today.get("uvIndex")

    if key == "max_temp":
        return extract_temp_value(today.get("maxTemp"))

    if key == "min_temp":
        return extract_temp_value(today.get("minTemp"))

    if key == "sunrise":
        return today.get("sunRise")

    if key == "sunset":
        return today.get("sunSet")

    # Time-aware sensors
    period = _period(data)

    if key == "wind_speed_mph":
        val = today.get(f"windspeedMph{period}")
        return int(val) if val is not None else None

    if key == "wind_speed_knots":
        val = today.get(f"windspeedKnots{period}")
        return int(val) if val is not None else None

    if key == "wind_speed_kph":
        val = today.get(f"windspeedKM{period}")
        return int(val) if val is not None else None

    if key == "wind_direction":
        return today.get(f"windDirection{period}", today.get("windDirection"))

    if key == "wind_force":
        return today.get(f"windSpeedForce{period}", today.get("windSpeed"))

    if key == "rain_probability":
        val = today.get(f"rainProb{period}")
        return int(val) if val is not None else None

    if key == "forecast_summary":
        desc_period = _desc_period(data)
        return today.get(f"{desc_period}Descripiton")  # API typo preserved

    if key == "confidence":
        return today.get(f"confidence{period}")

    return None


# Mapping from sensor key to (api_field, value_transformer) for future-aware daily sensors
_DAILY_FIELDS: dict[str, tuple[str, Any]] = {
    "uv_index": ("uvIndex", None),
    "max_temp": ("maxTemp", extract_temp_value),
    "min_temp": ("minTemp", extract_temp_value),
    "sunrise": ("sunRise", None),
    "sunset": ("sunSet", None),
}

# Mapping from sensor key to (morning_field, afternoon_field, evening_field)
_TIME_AWARE_FIELDS: dict[str, tuple[str, str, str]] = {
    "wind_speed_mph": ("windspeedMphMorning", "windspeedMphAfternoon", "windspeedMphEvening"),
    "wind_speed_knots": ("windspeedKnotsMorning", "windspeedKnotsAfternoon", "windspeedKnotsEvening"),
    "wind_speed_kph": ("windspeedKMMorning", "windspeedKMAfternoon", "windspeedKMEvening"),
    "wind_direction": ("windDirectionMorning", "windDirectionAfternoon", "windDirectionEvening"),
    "wind_force": ("windSpeedForceMorning", "windSpeedForceAfternoon", "windSpeedForceEvening"),
    "rain_probability": ("rainProbMorning", "rainProbAfternoon", "rainProbEvening"),
    "forecast_summary": ("morningDescripiton", "afternoonDescripiton", "nightDescripiton"),
    "confidence": ("confidenceMorning", "confidenceAfternoon", "confidenceEvening"),
}


def _get_extra_attributes(key: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """
    Build extra state attributes for time-aware and future-aware sensors.

    Time-aware: today's remaining periods + all three periods for days 2–6.
    Future-aware: single value per day for days 2–6.
    """
    forecast_days: list[dict[str, Any]] = data.get("forecastDay", [])

    if key in _DAILY_FIELDS:
        if len(forecast_days) <= 1:
            return None
        api_field, transformer = _DAILY_FIELDS[key]
        attrs: dict[str, Any] = {}
        for day_data in forecast_days[1 : min(6, len(forecast_days))]:
            day_label: str = day_data.get("dayName") or day_data.get("forecastDate", "Unknown")
            raw = day_data.get(api_field)
            attrs[day_label] = transformer(raw) if transformer else raw
        return attrs or None

    if key not in _TIME_AWARE_FIELDS:
        return None
    if len(forecast_days) <= 1:
        return None

    morning_key, afternoon_key, evening_key = _TIME_AWARE_FIELDS[key]
    attrs: dict[str, Any] = {}
    current_hour = datetime.now().hour
    forecast_date: str | None = data.get("forecastDate")

    # Today's remaining periods
    today = forecast_days[0]
    today_name: str = today.get("dayName", "Today")

    if not should_use_evening_data(forecast_date):
        show_afternoon = current_hour < 12
        show_evening = current_hour < 18
        if show_afternoon:
            attrs[f"{today_name} Afternoon"] = today.get(afternoon_key)
        if show_evening:
            attrs[f"{today_name} Evening"] = today.get(evening_key)

    # Future days — all three periods
    for day_data in forecast_days[1 : min(6, len(forecast_days))]:
        day_label: str = day_data.get("dayName") or day_data.get("forecastDate", "Unknown")
        attrs[f"{day_label} Morning"] = day_data.get(morning_key)
        attrs[f"{day_label} Afternoon"] = day_data.get(afternoon_key)
        attrs[f"{day_label} Evening"] = day_data.get(evening_key)

    return attrs or None


class GOVJEWeatherSensor(GOVJEWeatherEntity, SensorEntity):
    """A single GOV.JE Weather sensor entity."""

    entity_description: GOVJEWeatherSensorEntityDescription

    def __init__(
        self,
        coordinator: GOVJEWeatherDataUpdateCoordinator,
        entity_description: GOVJEWeatherSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)

    @property
    def native_value(self) -> Any:
        """Return the sensor state."""
        if not self.coordinator.data:
            return None
        return _get_native_value(self.entity_description.key, self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes for time-aware and future-aware sensors."""
        desc = self.entity_description
        if not self.coordinator.data or not (desc.time_aware or desc.future_aware):
            return None
        return _get_extra_attributes(desc.key, self.coordinator.data)
