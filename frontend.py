import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from backend import CITY_METADATA, get_spark_summary_data, fetch_live_weather

# Page configuration
# Page configuration
st.set_page_config(
    page_title="WeatherPulse",
    page_icon="\u26C5",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* Pull content up to remove clumsy top gap */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
}

.stApp {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #eff6ff 100%) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1e293b !important;
}

/* Hide Streamlit default chrome & anchor links */
[data-testid="stSidebar"] { display: none; }
header { visibility: hidden; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
a.header-anchor, a.anchor-link, [data-testid="stHeaderActionElements"] {
    display: none !important;
}

/* Clean Header Typography */
.nav-title {
    font-size: 2.3rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #0284c7 0%, #2563eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.nav-sub {
    font-size: 0.88rem;
    color: #64748b;
    font-weight: 500;
    margin-top: 0.25rem;
    margin-bottom: 0.8rem;
}

/* Left Hero Card */
.hero-card {
    background: linear-gradient(145deg, #0284c7 0%, #0369a1 100%);
    color: #ffffff;
    border-radius: 24px;
    padding: 2.2rem;
    box-shadow: 0 20px 40px -10px rgba(2, 132, 199, 0.35);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
}

.hero-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(8px);
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    width: fit-content;
}

.condition-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 700;
    color: #ffffff;
}

.hero-temp {
    font-size: 4.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    margin: 1.2rem 0 0.4rem 0;
}

.hero-desc {
    font-size: 1.1rem;
    font-weight: 600;
    opacity: 0.95;
}

/* Metric Highlight Cards */
.metric-card {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 20px;
    padding: 1.4rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
}

.metric-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #94a3b8;
}

.metric-val {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
}

.metric-sub {
    font-size: 0.8rem;
    font-weight: 500;
    color: #64748b;
    margin-top: 0.4rem;
}

/* Historical Chart Containers */
.chart-container-card {
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 24px;
    padding: 1.8rem;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.04);
    margin-top: 1.5rem;
}

.chart-header-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.2rem;
}

.chart-header-desc {
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 1rem;
}
</style>""", unsafe_allow_html=True)

# ----------------- Top Header Row (Elevated & De-cluttered) -----------------
nav_left, nav_right = st.columns([3, 1])

with nav_left:
    st.markdown('<div class="nav-title">WeatherPulse</div><div class="nav-sub">Real-Time Telemetry & Historical Climate Analytics</div>', unsafe_allow_html=True)

with nav_right:
    city_list = list(CITY_METADATA.keys())
    selected_city = st.selectbox("Select Station Location", city_list, index=0)

today_str = datetime.now().strftime("%A, %d %B")

# Fetch Live Weather
live = fetch_live_weather(selected_city)
curr_temp = live.get('temperature_2m', '--') if live else '--'
humidity = live.get('relative_humidity_2m', '--') if live else '--'
wind = live.get('wind_speed_10m', '--') if live else '--'
pressure = live.get('surface_pressure', '--') if live else '--'

# Pure CSS Status Dot using HTML character entities
if curr_temp != '--' and float(curr_temp) >= 35.0:
    condition_badge = '<span style="color: #f87171; font-size: 1rem; line-height: 1;">&#9679;</span> Elevated Thermal Index'
elif curr_temp != '--' and float(curr_temp) >= 28.0:
    condition_badge = '<span style="color: #fbbf24; font-size: 1rem; line-height: 1;">&#9679;</span> Warm & Clear'
elif humidity != '--' and float(humidity) >= 75.0:
    condition_badge = '<span style="color: #38bdf8; font-size: 1rem; line-height: 1;">&#9679;</span> High Saturation'
else:
    condition_badge = '<span style="color: #34d399; font-size: 1rem; line-height: 1;">&#9679;</span> Standard Atmospheric'

# Load Historical Summary Data
summary_df = get_spark_summary_data(selected_city)

# Calculate historical bounds for the hero card
all_time_max = summary_df["peak_max_temp"].max() if summary_df is not None and not summary_df.empty else "--"
all_time_min = summary_df["lowest_min_temp"].min() if summary_df is not None and not summary_df.empty else "--"

# ----------------- Hero + Metrics Grid -----------------
col_hero, col_metrics = st.columns([1.2, 2.4])

with col_hero:
    hero_html = f"""<div class="hero-card">
<div>
<div style="display:flex; justify-content:space-between; align-items:center;">
<div class="hero-badge">{selected_city} Station</div>
<div class="condition-pill">{condition_badge}</div>
</div>
<div class="hero-temp">{curr_temp}°<span style="font-size:2.2rem; font-weight:600;">C</span></div>
<div class="hero-desc">{today_str}</div>
</div>
<div style="margin-top: 1.8rem; padding-top: 1.2rem; border-top: 1px solid rgba(255, 255, 255, 0.25);">
<div style="display:flex; justify-content:space-between; font-size:0.85rem; opacity:0.95;">
<span>Historical Peak Extreme:</span>
<span style="font-weight:700;">{all_time_max} °C</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; opacity:0.95; margin-top:0.4rem;">
<span>Historical Lowest Extreme:</span>
<span style="font-weight:700;">{all_time_min} °C</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; opacity:0.95; margin-top:0.4rem;">
<span>Sensor Height:</span>
<span style="font-weight:700;">2m Surface Standard</span>
</div>
</div>
</div>"""
    st.markdown(hero_html, unsafe_allow_html=True)

with col_metrics:
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.markdown(f"""<div class="metric-card">
<div class="metric-header"><span class="metric-label">Relative Humidity</span></div>
<div class="metric-val">{humidity}<span style="font-size:1.2rem; color:#0284c7;"> %</span></div>
<div class="metric-sub">Atmospheric moisture content</div>
</div>""", unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f"""<div class="metric-card">
<div class="metric-header"><span class="metric-label">Wind Velocity</span></div>
<div class="metric-val">{wind}<span style="font-size:1.1rem; color:#0284c7;"> km/h</span></div>
<div class="metric-sub">Standard 10-meter elevation</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown(f"""<div class="metric-card">
<div class="metric-header"><span class="metric-label">Barometric Pressure</span></div>
<div class="metric-val">{pressure}<span style="font-size:1.1rem; color:#0284c7;"> hPa</span></div>
<div class="metric-sub">Sea-level adjusted reference</div>
</div>""", unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f"""<div class="metric-card">
<div class="metric-header"><span class="metric-label">Telemetry Status</span></div>
<div class="metric-val" style="color:#059669; font-size:1.6rem;"><span style="color:#10b981; font-size:1.2rem;">&#9679;</span> Nominal</div>
<div class="metric-sub">Real-time polling active</div>
</div>""", unsafe_allow_html=True)

# ----------------- Historical Analytical Graphs -----------------
if summary_df is not None and not summary_df.empty:
    st.markdown('<div class="chart-container-card"><div class="chart-header-title">Historical Temperature Trajectory (2000–2024 Records)</div><div class="chart-header-desc">Monthly Maximum Peak Extremes vs. Lowest Recorded Minimums</div>', unsafe_allow_html=True)
    
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=summary_df["date"], 
        y=summary_df["peak_max_temp"], 
        mode="lines", 
        name="Peak Max Temp (°C)", 
        line=dict(color="#f43f5e", width=2.2),
        fill='tonexty',
        fillcolor='rgba(244, 63, 94, 0.05)'
    ))
    fig_temp.add_trace(go.Scatter(
        x=summary_df["date"], 
        y=summary_df["lowest_min_temp"], 
        mode="lines", 
        name="Lowest Min Temp (°C)", 
        line=dict(color="#0284c7", width=2.2)
    ))
    fig_temp.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=340,
        margin=dict(l=40, r=20, t=20, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12, color="#475569")),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#64748b")),
        yaxis=dict(title="Temperature (°C)", showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#64748b"))
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-container-card"><div class="chart-header-title">Cumulative Monthly Precipitation History</div><div class="chart-header-desc">Aggregated Precipitation (Rainfall in mm) Time-Series Ledger</div>', unsafe_allow_html=True)

    fig_rain = px.bar(
        summary_df, 
        x="date", 
        y="total_precipitation",
        labels={"total_precipitation": "Precipitation (mm)", "date": "Timeline"},
        color_discrete_sequence=["#38bdf8"]
    )
    fig_rain.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=320,
        margin=dict(l=40, r=20, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#64748b")),
        yaxis=dict(title="Rainfall (mm)", showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#64748b"))
    )
    st.plotly_chart(fig_rain, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("View Processed Climate Ledger"):
        display_df = summary_df[["year", "month", "total_precipitation", "peak_max_temp", "lowest_min_temp", "avg_max_wind_speed"]].rename(columns={
            "year": "Year", "month": "Month", "total_precipitation": "Precipitation (mm)",
            "peak_max_temp": "Peak Max (°C)", "lowest_min_temp": "Lowest Min (°C)", "avg_max_wind_speed": "Wind (km/h)"
        })
        st.dataframe(display_df, use_container_width=True, height=220)
