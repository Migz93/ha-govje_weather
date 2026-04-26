"""Weather platform for govje_weather."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import re
from typing import TYPE_CHECKING, Any

from custom_components.govje_weather.const import (
    ATTRIBUTION,
    PARALLEL_UPDATES,
    TOOLTIP_CONDITION_MAP,
    WIND_DIRECTION_MAP,
    WIND_FORCE_TO_SPEED,
)
from custom_components.govje_weather.coordinator.data_processing import (
    extract_temp_value,
    get_time_period,
    should_use_evening_data,
)
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_IS_DAYTIME,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    CoordinatorWeatherEntity,
    Forecast,
)
from homeassistant.components.weather.const import WeatherEntityFeature
from homeassistant.const import UnitOfSpeed, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo

if TYPE_CHECKING:
    from custom_components.govje_weather.coordinator import GOVJEWeatherDataUpdateCoordinator
    from custom_components.govje_weather.data import GOVJEWeatherConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

__all__ = ["GOVJEWeatherEntity"]

# Re-export PARALLEL_UPDATES so HA picks it up for this platform
PARALLEL_UPDATES = PARALLEL_UPDATES  # noqa: PLW0127


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the GOV.JE weather entity."""
    async_add_entities(
        [GOVJEWeatherEntity(coordinator=entry.runtime_data.coordinator)],
        False,
    )


def _get_condition(tooltip: str | None) -> str | None:
    """Map a tooltip string to a HA weather condition."""
    if not tooltip:
        return None
    return TOOLTIP_CONDITION_MAP.get(tooltip)


def _get_bearing(direction: str | None) -> float | None:
    """Map a cardinal wind direction to a bearing in degrees."""
    if not direction:
        return None
    return WIND_DIRECTION_MAP.get(direction)


def _parse_day_name_to_iso(day_name: str | None) -> str:
    """
    Convert an API day name to an ISO 8601 datetime string at noon.

    Handles:
    - "Today"       -> current date
    - "Tomorrow"    -> current date + 1 day
    - "Sat 12 Jul"  -> nearest matching date
    """
    now = datetime.now(UTC)

    if day_name == "Today":
        return now.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

    if day_name == "Tomorrow":
        return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat()

    if day_name:
        match = re.match(r"\w+ (\d+) (\w+)", day_name)
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            month_map = {
                "Jan": 1,
                "Feb": 2,
                "Mar": 3,
                "Apr": 4,
                "May": 5,
                "Jun": 6,
                "Jul": 7,
                "Aug": 8,
                "Sep": 9,
                "Oct": 10,
                "Nov": 11,
                "Dec": 12,
            }
            month = month_map.get(month_str, now.month)
            year = now.year
            if month < now.month and month in (1, 2):
                year += 1
            try:
                return datetime(year, month, day, 12, 0, 0, tzinfo=UTC).isoformat()
            except ValueError:
                pass

    return now.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()


def _as_int(value: Any) -> int | None:
    """Return an integer from API data when possible."""
    if value in (None, ""):
        return None
    try:
        return int(value)
    except TypeError, ValueError:
        return None


def _as_float(value: Any) -> float | None:
    """Return a float from API data when possible."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except TypeError, ValueError:
        return None


def _daily_wind_speed_mph(day_data: dict[str, Any]) -> float | None:
    """Return the best daily wind speed value in mph."""
    direct_value = _as_float(day_data.get("windSpeedMPH"))
    if direct_value is not None:
        return direct_value

    period_values = [
        _as_float(day_data.get("windspeedMphMorning")),
        _as_float(day_data.get("windspeedMphAfternoon")),
        _as_float(day_data.get("windspeedMphEvening")),
    ]
    valid_period_values = [value for value in period_values if value is not None]
    if valid_period_values:
        return max(valid_period_values)

    wind_force = day_data.get("windSpeed")
    if not isinstance(wind_force, str):
        return None

    force_speed_ms = WIND_FORCE_TO_SPEED.get(wind_force)
    if force_speed_ms is None:
        return None
    return round(force_speed_ms * 2.23693629, 1)


def _build_daily_forecast(day_data: dict[str, Any]) -> Forecast:
    """Build a single Forecast object from one day's API data."""
    forecast: Forecast = Forecast(
        datetime=_parse_day_name_to_iso(day_data.get("dayName")),
        is_daytime=True,
    )

    condition = _get_condition(day_data.get("dayToolTip"))
    if condition:
        forecast[ATTR_FORECAST_CONDITION] = condition

    max_temp = extract_temp_value(day_data.get("maxTemp"))
    if max_temp is not None:
        forecast[ATTR_FORECAST_NATIVE_TEMP] = max_temp

    min_temp = extract_temp_value(day_data.get("minTemp"))
    if min_temp is not None:
        forecast[ATTR_FORECAST_NATIVE_TEMP_LOW] = min_temp

    # Use highest precipitation probability across all periods
    precip = max(
        _as_int(day_data.get("rainProbMorning")) or 0,
        _as_int(day_data.get("rainProbAfternoon")) or 0,
        _as_int(day_data.get("rainProbEvening")) or 0,
    )
    forecast[ATTR_FORECAST_PRECIPITATION_PROBABILITY] = precip

    bearing = _get_bearing(day_data.get("windDirection"))
    if bearing is not None:
        forecast[ATTR_FORECAST_WIND_BEARING] = bearing

    wind_speed = _daily_wind_speed_mph(day_data)
    if wind_speed is not None:
        forecast[ATTR_FORECAST_NATIVE_WIND_SPEED] = wind_speed

    forecast[ATTR_FORECAST_IS_DAYTIME] = True

    return forecast


class GOVJEWeatherEntity(CoordinatorWeatherEntity["GOVJEWeatherDataUpdateCoordinator"]):
    """Weather entity for the GOV.JE Weather integration."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = None  # Uses device name
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.MILES_PER_HOUR
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(self, coordinator: GOVJEWeatherDataUpdateCoordinator) -> None:
        """Initialise the weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_weather"
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

    @property
    def condition(self) -> str | None:
        """Return the current weather condition based on time of day."""
        data = self.coordinator.data
        if not data:
            return None
        forecast_days: list[dict[str, Any]] = data.get("forecastDay", [])
        if not forecast_days:
            return None

        forecast_date: str | None = data.get("forecastDate")
        today = forecast_days[0]

        if should_use_evening_data(forecast_date):
            tooltip_key = "iconEveningToolTip"
        else:
            period = get_time_period(forecast_date)
            tooltip_key = {
                "Morning": "iconMorningToolTip",
                "Afternoon": "iconAfternoonToolTip",
                "Evening": "iconEveningToolTip",
            }[period]

        tooltip = today.get(tooltip_key) or today.get("dayToolTip")
        return _get_condition(tooltip)

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        data = self.coordinator.data
        if not data:
            return None
        return extract_temp_value(data.get("currentTemprature"))

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing in degrees."""
        data = self.coordinator.data
        if not data:
            return None
        forecast_days: list[dict[str, Any]] = data.get("forecastDay", [])
        if not forecast_days:
            return None
        return _get_bearing(forecast_days[0].get("windDirection"))

    @property
    def native_wind_speed(self) -> float | None:
        """Return the time-of-day wind speed in mph."""
        data = self.coordinator.data
        if not data:
            return None
        forecast_days: list[dict[str, Any]] = data.get("forecastDay", [])
        if not forecast_days:
            return None

        forecast_date: str | None = data.get("forecastDate")
        today = forecast_days[0]

        if should_use_evening_data(forecast_date):
            key = "windspeedMphEvening"
        else:
            period = get_time_period(forecast_date)
            key = f"windspeedMph{period}"

        return _as_float(today.get(key) or today.get("windSpeedMPH"))

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        data = self.coordinator.data
        if not data:
            return None
        forecast_days: list[dict[str, Any]] = data.get("forecastDay", [])
        if not forecast_days:
            return None
        return [_build_daily_forecast(day) for day in forecast_days]
