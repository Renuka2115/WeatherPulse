import os
import glob
import pandas as pd
import requests
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

CITY_METADATA = {
    "Mumbai": {"coords": (19.0760, 72.8777), "aliases": ["mumbai"]},
    "Delhi": {"coords": (28.6139, 77.2090), "aliases": ["delhi"]},
    "Bengaluru": {"coords": (12.9716, 77.5946), "aliases": ["bengaluru", "bangalore"]},
    "Chennai": {"coords": (13.0827, 80.2707), "aliases": ["chennai", "madras"]},
    "Ahmedabad": {"coords": (23.0225, 72.5714), "aliases": ["ahmedabad"]},
    "Kolkata": {"coords": (22.5726, 88.3639), "aliases": ["kolkata", "calcutta"]}
}

def run_pyspark_pipeline():
    print("--- Initializing PySpark Session ---")
    spark = SparkSession.builder \
        .appName("WeatherAnalyticsEngine") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    base_dir = os.path.abspath(os.path.dirname(__file__))
    input_path = f"file://{os.path.join(base_dir, 'data', 'weather_data.csv')}"
    output_dir = f"file://{os.path.join(base_dir, 'output', 'monthly_weather_summary')}"

    print(f"Reading dataset: {input_path}")
    df = spark.read.csv(input_path, header=True, inferSchema=True)

    # 1. Feature Engineering
    df = df.withColumn("date", F.to_date("date", "yyyy-MM-dd")) \
           .withColumn("mean_temp", (F.col("temperature_2m_max") + F.col("temperature_2m_min")) / 2.0)

    # 2. Window Function: 7-Day Rolling Moving Average per City
    city_window = Window.partitionBy("city").orderBy("date").rowsBetween(-6, Window.currentRow)
    df_windowed = df.withColumn("7_day_moving_avg_temp", F.round(F.avg("mean_temp").over(city_window), 2))

    # 3. Monthly Aggregations
    df_monthly = df_windowed.withColumn("year", F.year("date")) \
                            .withColumn("month", F.month("date")) \
                            .groupBy("city", "year", "month") \
                            .agg(
                                F.round(F.sum("precipitation_sum"), 2).alias("total_precipitation"),
                                F.round(F.max("temperature_2m_max"), 2).alias("peak_max_temp"),
                                F.round(F.min("temperature_2m_min"), 2).alias("lowest_min_temp"),
                                F.round(F.avg("wind_speed_10m_max"), 2).alias("avg_max_wind_speed")
                            ) \
                            .orderBy("city", "year", "month")

    # 4. Save to Output Directory
    df_monthly.coalesce(1).write.mode("overwrite").csv(output_dir, header=True)
    print("--- PySpark Pipeline Completed Successfully ---")
    spark.stop()

def get_spark_summary_data(city_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    summary_dir = os.path.join(base_dir, "output", "monthly_weather_summary")
    csv_files = glob.glob(os.path.join(summary_dir, "*.csv"))
    
    if not csv_files:
        return None
    
    df = pd.read_csv(csv_files[0])
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-01")
    
    aliases = CITY_METADATA.get(city_name, {}).get("aliases", [city_name.lower()])
    city_df = df[df["city"].str.strip().str.lower().isin(aliases)].sort_values("date")
    return city_df

def fetch_live_weather(city_name):
    city_data = CITY_METADATA.get(city_name)
    if not city_data:
        return None
    lat, lon = city_data["coords"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,weather_code"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("current", {})
    except Exception:
        pass
    return None

if __name__ == "__main__":
    run_pyspark_pipeline()
