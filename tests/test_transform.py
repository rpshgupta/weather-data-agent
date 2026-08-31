from datetime import datetime, timezone

from weather_data_agent.transform import to_bronze_record


def test_to_bronze_record_flattens_current_fields():
    weather = {
        "current": {
            "time": "2026-08-31T12:00",
            "interval": 900,
            "temperature_2m": 18.4,
            "relative_humidity_2m": 62,
            "wind_speed_10m": 11.2,
        }
    }
    timestamp = datetime(2026, 8, 31, 12, 5, tzinfo=timezone.utc)

    record = to_bronze_record(
        weather,
        latitude=52.3676,
        longitude=4.9041,
        source_system="open-meteo",
        ingestion_timestamp=timestamp,
    )

    assert record == {
        "latitude": 52.3676,
        "longitude": 4.9041,
        "time": "2026-08-31T12:00",
        "interval": 900,
        "temperature_2m": 18.4,
        "relative_humidity_2m": 62,
        "wind_speed_10m": 11.2,
        "ingestion_timestamp": timestamp,
        "source_system": "open-meteo",
    }


def test_to_bronze_record_uses_requested_coordinates_not_response():
    weather = {"latitude": 999.0, "longitude": -999.0, "current": {}}
    timestamp = datetime(2026, 8, 31, tzinfo=timezone.utc)

    record = to_bronze_record(
        weather,
        latitude=52.3676,
        longitude=4.9041,
        source_system="open-meteo",
        ingestion_timestamp=timestamp,
    )

    assert record["latitude"] == 52.3676
    assert record["longitude"] == 4.9041


def test_to_bronze_record_handles_missing_current_key():
    timestamp = datetime(2026, 8, 31, tzinfo=timezone.utc)

    record = to_bronze_record(
        {},
        latitude=52.3676,
        longitude=4.9041,
        source_system="open-meteo",
        ingestion_timestamp=timestamp,
    )

    assert record == {
        "latitude": 52.3676,
        "longitude": 4.9041,
        "ingestion_timestamp": timestamp,
        "source_system": "open-meteo",
    }
