from weather_data_agent.ingestion import fetch_weather


def test_fetch_weather():
    result = fetch_weather(
        latitude=52.3676,
        longitude=4.9041,
    )

    assert "current" in result
    assert "temperature_2m" in result["current"]