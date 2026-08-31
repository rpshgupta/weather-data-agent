from weather_data_agent.ingestion import fetch_weather


def main() -> None:
    weather = fetch_weather(latitude=52.3676, longitude=4.9041)
    print(weather)
