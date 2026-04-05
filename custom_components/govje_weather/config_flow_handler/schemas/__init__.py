"""
Data schemas for config flow forms.

Contains voluptuous schemas used in config and options flows.
"""

from __future__ import annotations

from custom_components.govje_weather.config_flow_handler.schemas.options import get_options_schema

__all__ = [
    "get_options_schema",
]
