from datetime import datetime
from typing import Any


def to_bronze_record(
    weather: dict[str, Any],
    *,
    latitude: float,
    longitude: float,
    source_system: str,
    ingestion_timestamp: datetime,
) -> dict[str, Any]:
    """Flatten a raw Open-Meteo `current weather` response into a bronze row.

    `latitude`/`longitude` are taken from the request (not echoed back by the
    API) so the record stays correct even if a response omits them.
    """
    current = weather.get("current", {})

    return {
        "latitude": latitude,
        "longitude": longitude,
        **current,
        "ingestion_timestamp": ingestion_timestamp,
        "source_system": source_system,
    }
