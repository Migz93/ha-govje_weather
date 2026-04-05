"""
Entity package for govje_weather.

Architecture:
    All platform entities inherit from (PlatformEntity, GOVJEWeatherEntity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the GOVJEWeatherEntity base class.
"""

from .base import GOVJEWeatherEntity

__all__ = ["GOVJEWeatherEntity"]
