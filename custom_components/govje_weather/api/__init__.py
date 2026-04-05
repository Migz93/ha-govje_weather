"""
API package for govje_weather.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Exception hierarchy:
    GOVJEWeatherApiClientError (base)
    └── GOVJEWeatherApiClientCommunicationError (network/timeout/HTTP error)
"""

from .client import GOVJEWeatherApiClient, GOVJEWeatherApiClientCommunicationError, GOVJEWeatherApiClientError

__all__ = [
    "GOVJEWeatherApiClient",
    "GOVJEWeatherApiClientCommunicationError",
    "GOVJEWeatherApiClientError",
]
