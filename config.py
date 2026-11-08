"""
Configuration settings, constants, city coordinates, and weather codes
for the Travel Planning Assistant.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
FLIGHTS_FILE = BASE_DIR / "flights.json"
HOTELS_FILE = BASE_DIR / "hotels.json"
PLACES_FILE = BASE_DIR / "places.json"
BUSES_FILE = BASE_DIR / "buses.json"
CABS_FILE = BASE_DIR / "cabs.json"

# Open-Meteo REST API Endpoint (Free, no API key required)
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Geographic Coordinates for Supported Indian Hub Cities
CITY_COORDINATES = {
    "Goa": {"latitude": 15.2993, "longitude": 74.1240},
    "Delhi": {"latitude": 28.6139, "longitude": 77.2090},
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "Bangalore": {"latitude": 12.9716, "longitude": 77.5946},
    "Chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "Hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
    "Jaipur": {"latitude": 26.9124, "longitude": 75.7873},
    "Kolkata": {"latitude": 22.5726, "longitude": 88.3639},
}

# WMO Weather Interpretation Codes (Open-Meteo standard)
WMO_WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow fall ❄️",
    73: "Moderate snow fall ❄️",
    75: "Heavy snow fall ❄️",
    77: "Snow grains ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    85: "Slight snow showers ❄️",
    86: "Heavy snow showers ❄️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

# Daily local expense estimates (food, local transit, entry tickets) in INR
DAILY_EXPENSE_TIERS = {
    "budget": 800,
    "moderate": 1500,
    "luxury": 3000,
}

# Default Trip Configuration
DEFAULT_NUM_DAYS = 3
DEFAULT_TRAVEL_STYLE = "moderate"

