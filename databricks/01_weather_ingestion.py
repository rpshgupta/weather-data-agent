# Databricks notebook source
# MAGIC %md
# MAGIC # Weather Ingestion — Bronze
# MAGIC Fetches current weather for Amsterdam from Open-Meteo (via `WeatherClient`) and
# MAGIC appends it to the `weather_bronze` Delta table.
# MAGIC
# MAGIC Re-running this notebook is safe: each run appends one new row stamped with its
# MAGIC own `ingestion_timestamp`, so bronze history is preserved rather than overwritten.

# COMMAND ----------

# MAGIC %pip install -e ..

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import logging
from datetime import datetime, timezone

from weather_data_agent.ingestion import WeatherAPIError, WeatherClient
from weather_data_agent.transform import to_bronze_record

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_bronze_ingestion")

LATITUDE = 52.3676
LONGITUDE = 4.9041
SOURCE_SYSTEM = "open-meteo"
BRONZE_TABLE = "weather_bronze"

# COMMAND ----------

client = WeatherClient()

try:
    weather = client.fetch_current_weather(latitude=LATITUDE, longitude=LONGITUDE)
except WeatherAPIError as exc:
    raise RuntimeError(f"Weather ingestion failed: {exc}") from exc

record = to_bronze_record(
    weather,
    latitude=LATITUDE,
    longitude=LONGITUDE,
    source_system=SOURCE_SYSTEM,
    ingestion_timestamp=datetime.now(timezone.utc),
)

# COMMAND ----------

bronze_df = spark.createDataFrame([record])

# `append` keeps bronze append-only and history-preserving; the table is
# created automatically on first run and reused on every run after that.
bronze_df.write.format("delta").mode("append").saveAsTable(BRONZE_TABLE)

logger.info("Appended 1 row to %s", BRONZE_TABLE)
display(bronze_df)
