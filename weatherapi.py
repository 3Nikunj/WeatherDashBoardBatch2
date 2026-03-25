import streamlit as st
import requests

# geocoding API: help to convert location name to lat and long
# weather API: help to get the weather data for a given lat and long

st.set_page_config(page_title="Weather App",
                   page_icon=":sunny:", layout="wide")

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    90: "Thunderstorm with slight rain",
    91: "Thunderstorm with moderate rain",
    92: "Thunderstorm with heavy rain",
    95: "Thunderstorm with slight or moderate rain",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def get_wmo(code):   # 94
    return WMO_CODES.get(code, "Unknown weather condition")


def wind_direction(degree):
    list = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    # deg = round(degree/45) % 8
    # return list[deg]
    return list[round(degree/45) % 8]

# API Calls


def geocode(city):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 5, "language": "en",
                "format": "json"}, timeout=8,
    )
    r.raise_for_status()  # 200:success , 300: redirection,
    # 400: client error, 500: server error
    return r.json().get("results", [])


def fetch_weather(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "weather_code",
                "precipitation",
                "uv_index",
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "uv_index_max",
                "weather_code",
            ],
            "hourly": [
                "temperature_2m",
                "precipitation_probability",
            ],
            "timezone": "auto",
            "forecast_days": 7
        }, timeout=10,
    )
    r.raise_for_status()
    return r.json()


# UI Components
st.title("Weather App :sunny:")
st.caption("Get the current weather and 7-day forecast for any city "
           "in the world.")

city_input = st.text_input("Enter a city name",
                           placeholder="e.g. New York, Tokyo, Paris")

unit = st.radio("Select temperature unit", ("Celsius", "Fahrenheit"),
                horizontal=True)

if not city_input:
    st.info("Please enter a city name to get the weather information.")
    st.stop()

with st.spinner("Fetching location data..."):
    try:
        results = geocode(city_input)
    except Exception as e:
        st.error(f"Geocode Failed: {e}")
        st.stop()

if not results:
    st.error("No location found. Please check the city name and "
             "try again.")
    st.stop()

options = [
    f"{r['name']}, {r.get('admin1', '')}, {r['country']}" for r in results
]
selected = st.selectbox("Select the correct location",
                        range(len(options)),
                        format_func=lambda x: options[x])
loc = results[selected]

with st.spinner("Fetching weather data..."):
    try:
        data = fetch_weather(loc["latitude"], loc["longitude"])
    except Exception as e:
        st.error(f"Weather Fetch Failed: {e}")
        st.stop()

cur = data["current"]
daily = data["daily"]
hourly = data["hourly"]


def fmt(c):
    return round(c*9/5 + 32, 1) if unit == "Fahrenheit" else c


# Current Weather
st.divider()
st.subheader(f"Current Weather -- {options[selected]}")
st.metric("Temperature", f"{fmt(cur['temperature_2m'])}°{unit}",
          f"Feels like {fmt(cur['apparent_temperature'])}°{unit}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Humidity", f"{cur['relative_humidity_2m']}%")
with col2:
    st.metric("Wind Speed", f"{cur['wind_speed_10m']} km/h"
              f"({wind_direction(cur['wind_direction_10m'])})")
with col3:
    st.metric("Precipitation", f"{cur['precipitation']} mm")
with col4:
    st.metric("UV Index", f"{cur['uv_index']}")

st.caption(f"Conditions:  {get_wmo(cur["weather_code"])}")
