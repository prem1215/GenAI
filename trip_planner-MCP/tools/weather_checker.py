import requests

def get_weather_summary(lat: float, lon: float) -> str:
    """Return a short weather summary for the given coordinate using US NWS.
    If outside the US (or failure), return a soft error string.
    """
    try:
        r = requests.get(f"https://api.weather.gov/points/{lat},{lon}", timeout=10)
        if r.status_code != 200:
            return "Weather unavailable"
        props = r.json().get("properties", {})
        hourly_url = props.get("forecastHourly")
        if not hourly_url:
            return "Weather unavailable"
        data = requests.get(hourly_url, timeout=10).json()
        periods = data.get("properties", {}).get("periods", [])
        if not periods:
            return "Weather unavailable"
        p0 = periods[0]
        temp = p0.get("temperature")
        unit = p0.get("temperatureUnit", "F")
        short = p0.get("shortForecast", "N/A")
        return f"{short}, {temp}°{unit}"
    except Exception:
        return "Weather unavailable"
