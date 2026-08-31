import logging
from typing import Any, Optional, Sequence

import requests

logger = logging.getLogger(__name__)

DEFAULT_CURRENT_FIELDS: tuple[str, ...] = (
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
)


class WeatherAPIError(Exception):
    """Raised when a request to the weather API fails or returns bad data."""


class WeatherClient:
    """Client for fetching weather data from the Open-Meteo API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()

    def fetch_current_weather(
        self,
        latitude: float,
        longitude: float,
        fields: Sequence[str] = DEFAULT_CURRENT_FIELDS,
    ) -> dict[str, Any]:
        """Fetch current weather conditions for a given location.

        Raises:
            WeatherAPIError: if the request times out, fails, or returns
                a response that cannot be parsed as JSON.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": list(fields),
        }

        logger.info(
            "Fetching current weather (lat=%s, lon=%s, fields=%s)",
            latitude,
            longitude,
            fields,
        )

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            logger.error(
                "Timed out fetching weather data after %s seconds", self.timeout
            )
            raise WeatherAPIError(
                f"Request to Open-Meteo timed out after {self.timeout}s"
            ) from exc
        except requests.RequestException as exc:
            logger.error("Failed to fetch weather data: %s", exc)
            raise WeatherAPIError(f"Failed to fetch weather data: {exc}") from exc

        try:
            data: dict[str, Any] = response.json()
        except ValueError as exc:
            logger.error("Received invalid JSON from Open-Meteo: %s", exc)
            raise WeatherAPIError(
                f"Invalid JSON response from Open-Meteo: {exc}"
            ) from exc

        logger.debug("Received weather data: %s", data)
        return data
