# WeatherPulse — Meteorological Analytics & Telemetry Engine

WeatherPulse is a distributed meteorological intelligence dashboard combining historical time-series batch processing using **Apache Spark (PySpark)** with real-time live telemetry streaming via the **Open-Meteo REST API**, presented through an interactive **Streamlit** UI.

## Architecture & Technology Stack
- **Batch Processing Engine**: Apache Spark 3.5.3 (PySpark DataFrame & Window API)
- **Real-Time Telemetry**: Open-Meteo REST API (HTTP Polling)
- **Frontend / Presentation Layer**: Streamlit & Plotly (Express & Graph Objects)
- **Environment**: Python 3.12 running on WSL2 / Linux

## Features
- **Decoupled Architecture**: Separated analytical computations (`backend.py`) and UI presentation tier (`frontend.py`).
- **Distributed Aggregations**:
  - 7-day rolling window moving average temperature calculations partitioned by city.
  - Multi-year monthly climate aggregates (peak highs, record lows, cumulative precipitation).
- **Live Meteorological Stream**: Real-time ambient temperature, humidity, wind velocity, and barometric pressure.

## Setup & Running

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-github-username>/WeatherPulse.git
   cd WeatherPulse
