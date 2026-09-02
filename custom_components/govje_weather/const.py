"""Constants for govje_weather."""

from logging import Logger, getLogger

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
)

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "govje_weather"
ATTRIBUTION = "Data provided by Government of Jersey"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Data source
REMOTE_URL = "https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json"
WARNING_STATUS_URL = "https://prodgojweatherstorage.blob.core.windows.net/data/JerseyWarningStatusXML.json"

# Configuration keys
CONF_SCAN_INTERVAL = "scan_interval"

# Default configuration values
DEFAULT_SCAN_INTERVAL = 10  # minutes
MIN_SCAN_INTERVAL = 5  # minutes
MAX_SCAN_INTERVAL = 1440  # minutes (24 hours)

# Tooltip mappings based on the dayToolTip / iconXToolTip values in the JSON data.
# Maps the tooltip text to Home Assistant weather conditions.
# Collected over several months of real API data.
TOOLTIP_CONDITION_MAP: dict[str, str] = {
    "Sunny": ATTR_CONDITION_SUNNY,
    "Sunny and hot": ATTR_CONDITION_SUNNY,
    "Mainly sunny": ATTR_CONDITION_PARTLYCLOUDY,
    "Fine": ATTR_CONDITION_CLEAR_NIGHT,
    "Sunny periods": ATTR_CONDITION_PARTLYCLOUDY,
    "Cloudy, a few brighter spells": ATTR_CONDITION_PARTLYCLOUDY,
    "Cloudy a.m. Sunny p.m.": ATTR_CONDITION_PARTLYCLOUDY,
    "Sunny a.m. Cloudy p.m.": ATTR_CONDITION_PARTLYCLOUDY,
    "Sunny a.m. Rain p.m.": ATTR_CONDITION_RAINY,
    "Rain later": ATTR_CONDITION_RAINY,
    "Rain a.m. Sunny p.m.": ATTR_CONDITION_RAINY,
    "Rain": ATTR_CONDITION_RAINY,
    "Fair": ATTR_CONDITION_PARTLYCLOUDY,
    "Fair periods and showers": ATTR_CONDITION_RAINY,
    "Sunshine and showers": ATTR_CONDITION_RAINY,
    "Sunshine and heavy shower": ATTR_CONDITION_RAINY,
    "Cloudy with showers": ATTR_CONDITION_RAINY,
    "Rain at times": ATTR_CONDITION_POURING,
    "Heavy rain at times": ATTR_CONDITION_POURING,
    "Rain clearing": ATTR_CONDITION_RAINY,
    "Sleet at times": ATTR_CONDITION_SNOWY_RAINY,
    "Very windy": ATTR_CONDITION_WINDY,
    "Stormy": ATTR_CONDITION_LIGHTNING_RAINY,
    "Isolated thunderstorms": ATTR_CONDITION_LIGHTNING_RAINY,
    "Cloudy": ATTR_CONDITION_CLOUDY,
    "Windy": ATTR_CONDITION_WINDY,
    "Drizzle": ATTR_CONDITION_RAINY,
    "Fog": ATTR_CONDITION_FOG,
    "Misty": ATTR_CONDITION_FOG,
}

# Wind direction mappings: cardinal/intercardinal to bearing degrees
WIND_DIRECTION_MAP: dict[str, float] = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}

# Beaufort force scale to approximate speed in m/s
WIND_FORCE_TO_SPEED: dict[str, float] = {
    "F0": 0.0,  # Calm
    "F1": 0.5,  # Light air
    "F2": 2.0,  # Light breeze
    "F3": 4.0,  # Gentle breeze
    "F4": 6.0,  # Moderate breeze
    "F5": 9.0,  # Fresh breeze
    "F6": 12.0,  # Strong breeze
    "F7": 15.0,  # Near gale
    "F8": 19.0,  # Gale
    "F9": 23.0,  # Strong gale
    "F10": 27.0,  # Storm
    "F11": 31.0,  # Violent storm
    "F12": 34.0,  # Hurricane
}
