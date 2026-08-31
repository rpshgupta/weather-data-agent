from unittest.mock import MagicMock

import pytest
import requests

from weather_data_agent.ingestion import DEFAULT_CURRENT_FIELDS, WeatherAPIError, WeatherClient


def make_client(session: MagicMock) -> WeatherClient:
    return WeatherClient(timeout=5.0, session=session)


def test_fetch_current_weather_returns_parsed_json():
    session = MagicMock()
    session.get.return_value.json.return_value = {
        "current": {
            "temperature_2m": 18.4,
            "relative_humidity_2m": 62,
            "wind_speed_10m": 11.2,
        }
    }

    client = make_client(session)
    result = client.fetch_current_weather(latitude=52.3676, longitude=4.9041)

    assert "current" in result
    assert result["current"]["temperature_2m"] == 18.4


def test_fetch_current_weather_sends_expected_params():
    session = MagicMock()
    session.get.return_value.json.return_value = {"current": {}}

    client = make_client(session)
    client.fetch_current_weather(latitude=52.3676, longitude=4.9041)

    _, kwargs = session.get.call_args
    assert kwargs["params"]["latitude"] == 52.3676
    assert kwargs["params"]["longitude"] == 4.9041
    assert kwargs["params"]["current"] == list(DEFAULT_CURRENT_FIELDS)
    assert kwargs["timeout"] == 5.0


def test_fetch_current_weather_supports_custom_fields():
    session = MagicMock()
    session.get.return_value.json.return_value = {"current": {}}

    client = make_client(session)
    client.fetch_current_weather(
        latitude=52.3676, longitude=4.9041, fields=["temperature_2m"]
    )

    _, kwargs = session.get.call_args
    assert kwargs["params"]["current"] == ["temperature_2m"]


def test_fetch_current_weather_raises_on_timeout():
    session = MagicMock()
    session.get.side_effect = requests.Timeout("timed out")

    client = make_client(session)
    with pytest.raises(WeatherAPIError):
        client.fetch_current_weather(latitude=52.3676, longitude=4.9041)


def test_fetch_current_weather_raises_on_http_error():
    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = requests.HTTPError(
        "500 Server Error"
    )

    client = make_client(session)
    with pytest.raises(WeatherAPIError):
        client.fetch_current_weather(latitude=52.3676, longitude=4.9041)


def test_fetch_current_weather_raises_on_invalid_json():
    session = MagicMock()
    session.get.return_value.json.side_effect = ValueError("not json")

    client = make_client(session)
    with pytest.raises(WeatherAPIError):
        client.fetch_current_weather(latitude=52.3676, longitude=4.9041)


def test_weather_client_uses_provided_session_and_timeout():
    session = MagicMock()
    client = WeatherClient(timeout=12.5, session=session)

    assert client.session is session
    assert client.timeout == 12.5


def test_weather_client_defaults_to_own_session():
    client = WeatherClient()

    assert isinstance(client.session, requests.Session)
