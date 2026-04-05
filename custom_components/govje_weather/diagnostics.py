"""Diagnostics support for govje_weather.

Learn more about diagnostics:
https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import GOVJEWeatherConfigEntry

# No sensitive fields for this integration (public API, no credentials).
# Listed for completeness in case options grow in future.
TO_REDACT: set[str] = set()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: GOVJEWeatherConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for the GOV.JE Weather config entry."""
    coordinator = entry.runtime_data.coordinator
    integration = entry.runtime_data.integration

    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

    devices = dr.async_entries_for_config_entry(device_reg, entry.entry_id)
    device_info = []
    for device in devices:
        entities = er.async_entries_for_device(entity_reg, device.id)
        device_info.append(
            {
                "id": device.id,
                "name": device.name,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "entity_count": len(entities),
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "platform": entity.platform,
                        "original_name": entity.original_name,
                        "disabled": entity.disabled,
                    }
                    for entity in entities
                ],
            }
        )

    coordinator_info = {
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "forecast_date": coordinator.data.get("forecastDate") if coordinator.data else None,
        "forecast_days": len(coordinator.data.get("forecastDay", [])) if coordinator.data else 0,
    }

    integration_info = {
        "name": integration.name,
        "version": integration.version,
        "domain": integration.domain,
        "documentation": integration.documentation,
    }

    entry_info = {
        "entry_id": entry.entry_id,
        "version": entry.version,
        "domain": entry.domain,
        "title": entry.title,
        "state": str(entry.state),
        "unique_id": entry.unique_id,
        "data": async_redact_data(entry.data, TO_REDACT),
        "options": async_redact_data(entry.options, TO_REDACT),
    }

    error_info = {
        "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        "last_exception_type": (type(coordinator.last_exception).__name__ if coordinator.last_exception else None),
    }

    return {
        "entry": entry_info,
        "integration": integration_info,
        "coordinator": coordinator_info,
        "devices": device_info,
        "error": error_info,
    }
