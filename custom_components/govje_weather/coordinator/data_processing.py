"""
Data processing utilities for the GOV.JE Weather coordinator.

Provides time-of-day helpers used by both the weather entity and sensor entities
to select the correct morning/afternoon/evening data from the API response.

Time-of-day periods:
    Morning   - 05:00 to 11:59
    Afternoon - 12:00 to 17:59
    Evening   - 18:00 to 23:59, and 00:00 to 04:59

Midnight handling (00:00-04:59):
    If the API's forecastDate still reflects yesterday's date, the forecast
    hasn't been updated yet - show the previous evening's data.
    Once the forecast updates to today's date, switch to morning data.
"""

from __future__ import annotations

from datetime import datetime


def should_use_evening_data(forecast_date: str | None) -> bool:
    """
    Determine whether to show evening data during the 00:00-04:59 window.

    Between midnight and 05:00, the GOV.JE API may not yet have updated to
    the current date. In that case, continue showing the previous evening's
    data rather than switching to morning prematurely.

    Args:
        forecast_date: The forecastDate string from the API (e.g. "12 July 2025"),
            or None if not available.

    Returns:
        True if we are in the 00:00-04:59 window AND the forecast date
        does not match today's date (i.e. the forecast hasn't updated yet).
    """
    if not forecast_date:
        return False
    now = datetime.now()
    if not (0 <= now.hour < 5):
        return False
    today_str = now.strftime("%d %B %Y")
    return today_str != forecast_date


def get_time_period(forecast_date: str | None) -> str:
    """
    Return the current time-of-day period as used by the API field suffixes.

    Period    Hours        API suffix
    --------  -----------  ----------
    Morning   05:00-11:59  Morning
    Afternoon 12:00-17:59  Afternoon
    Evening   18:00-23:59  Evening
    Evening*  00:00-04:59  Evening (if forecast not yet updated)
    Morning*  00:00-04:59  Morning (if forecast already updated to today)

    Args:
        forecast_date: The forecastDate string from the API, or None.

    Returns:
        "Morning", "Afternoon", or "Evening".
    """
    if should_use_evening_data(forecast_date):
        return "Evening"
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Morning"
    if 12 <= current_hour < 18:
        return "Afternoon"
    return "Evening"


def get_description_period(forecast_date: str | None) -> str:
    """
    Return the description field prefix for the current time-of-day period.

    The API uses a different naming convention for description fields:
        morningDescripiton, afternoonDescripiton, nightDescripiton

    Args:
        forecast_date: The forecastDate string from the API, or None.

    Returns:
        "morning", "afternoon", or "night".
    """
    period = get_time_period(forecast_date)
    if period == "Morning":
        return "morning"
    if period == "Afternoon":
        return "afternoon"
    return "night"


def extract_temp_value(temp_str: str | None) -> float | None:
    """
    Extract a float temperature value from a string like "24°C".

    Args:
        temp_str: Temperature string from the API, e.g. "24°C", or None.

    Returns:
        The numeric temperature as a float, or None if parsing fails.
    """
    if not temp_str:
        return None
    try:
        return float(temp_str.replace("°C", "").strip())
    except ValueError, TypeError:
        return None
