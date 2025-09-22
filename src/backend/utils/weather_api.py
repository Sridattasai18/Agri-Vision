import os
import requests

def get_weather_data(city):
    """Get current weather data from OpenWeatherMap API"""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    if not api_key:
        return {"error": "Weather service is not configured. Please set the OPENWEATHER_API_KEY environment variable."}
    try:
        params = {'q': city, 'appid': api_key, 'units': 'metric'}
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        if response.status_code == 200:
            return {
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
                "city": data['name'],
                "country": data['sys']['country']
            }
        else:
            return {"error": f"Weather data not found for {city}"}
    except Exception as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

def get_coordinates(city: str):
    """Geocode a city name to latitude and longitude using Open-Meteo Geocoding API (no key)"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status() # Raise an exception for bad status codes
        results = r.json().get('results') or []
        if not results:
            return None
        first = results[0]
        return {"lat": first.get("latitude"), "lon": first.get("longitude"), "name": first.get("name"), "country": first.get("country", "")}
    except requests.exceptions.RequestException as e:
        print(f"Geocoding API error for {city}: {e}")
        return None

def get_weather_forecast(city: str):
    """Get 7-day daily weather forecast using Open-Meteo (no key)"""
    coords = get_coordinates(city)
    if not coords:
        return {"error": f"Could not find location for '{city}'"}
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,weather_code",
        "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json().get('daily', {})
        days = []
        for i, dt in enumerate(d.get('time', [])[:7]):
            days.append({
                "dt": dt,
                "temp_min": d.get('temperature_2m_min', [None])[i],
                "temp_max": d.get('temperature_2m_max', [None])[i],
                "humidity": d.get('relative_humidity_2m_mean', [None])[i],
                "weather_code": d.get('weather_code', [None])[i]
            })
        return {"success": True, "city": coords["name"], "country": coords.get("country", ""), "days": days}
    except requests.exceptions.RequestException as e:
        print(f"Forecast API error for {city}: {e}")
        return {"error": "Failed to fetch forecast"}

class WeatherAPIWrapper:
    """Wrapper to provide a consistent interface for weather data to the chatbot."""
    def get_current_weather(self, city):
        # This uses the OpenWeatherMap API for current conditions
        return get_weather_data(city)