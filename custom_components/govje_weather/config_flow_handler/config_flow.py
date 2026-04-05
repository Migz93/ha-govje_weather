"""
Config flow for govje_weather.

Single-instance integration — no credentials required. The user step
just confirms the setup and creates the entry.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.govje_weather.const import DOMAIN
from homeassistant import config_entries

if TYPE_CHECKING:
    from custom_components.govje_weather.config_flow_handler.options_flow import GOVJEWeatherOptionsFlow


class GOVJEWeatherConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Config flow for GOV.JE Weather.

    No credentials are needed — the API is a public endpoint.
    Only one instance of this integration is allowed.
    """

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GOVJEWeatherOptionsFlow:
        """Return the options flow handler."""
        from custom_components.govje_weather.config_flow_handler.options_flow import (  # noqa: PLC0415
            GOVJEWeatherOptionsFlow,
        )

        return GOVJEWeatherOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle the initial user setup step.

        No form inputs are required — simply confirm and create the entry.

        Args:
            user_input: Ignored; kept for API compatibility.

        Returns:
            The config flow result creating a new entry.
        """
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="GOV.JE Weather",
                data={},
            )

        return self.async_show_form(step_id="user")


__all__ = ["GOVJEWeatherConfigFlowHandler"]
