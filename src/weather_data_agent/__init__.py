import logging

from weather_data_agent.ingestion import WeatherAPIError, WeatherClient


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = WeatherClient()
    try:
        weather = client.fetch_current_weather(latitude=52.3676, longitude=4.9041)
    except WeatherAPIError as exc:
        print(f"Failed to fetch weather data: {exc}")
        return

    print(weather)
