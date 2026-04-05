"""
Options flow for govje_weather.

Allows users to change the data refresh interval after initial setup.
"""

from __future__ import annotations

from typing import Any

from custom_components.govje_weather.config_flow_handler.schemas import get_options_schema
from homeassistant import config_entries


class GOVJEWeatherOptionsFlow(config_entries.OptionsFlow):
    """
    Options flow for GOV.JE Weather.

    Presents a single form to configure the data refresh interval.
    """

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the options form.

        Args:
            user_input: Submitted form values, or None for initial display.

        Returns:
            The config flow result.
        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry.options),
        )


__all__ = ["GOVJEWeatherOptionsFlow"]
