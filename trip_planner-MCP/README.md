# RoadTrip MCP Server 🚗

A smart road trip planner that helps you plan safe and comfortable breaks during long drives. Built as a Model Context Protocol (MCP) server, it seamlessly integrates with AI assistants.

## Features

🛣️ **Smart Route Planning**
- Splits driving routes into comfortable segments using **Google Directions API**
- Considers live and predicted traffic conditions
- Customizable break intervals (default: 2 hours)

🏪 **Intelligent Stop Selection**
- Prioritizes **state rest areas** for safety and convenience
- Falls back to highly-rated restaurants from **Yelp** when rest areas aren't available
- Considers ratings, reviews, and accessibility

🌤️ **Weather Integration**
- Fetches real-time weather data from the **US National Weather Service**
- Provides current conditions for each stop
- Helps you plan for weather-appropriate breaks

🗺️ **Easy Sharing**
- Generates shareable **Google Maps URLs** with all your stops
- Compatible with mobile and desktop navigation
- Optimized to work within Google Maps' waypoint limits

## Quick Start

```bash
python -m venv venv
source venv/bin/activate   # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
cp .env.example .env       # fill in your keys
python main.py
```

You should see sample output in the console. This file also runs as an **MCP server**; connect it from an MCP-compatible client (e.g. Claude Desktop).

## Prerequisites

Before you begin, you'll need:

1. **Google Cloud Platform Account**
   - Create a project at [Google Cloud Console](https://console.cloud.google.com)
   - Enable these APIs:
     - Directions API
     - Places API
     - Geocoding API
   - Create an API key with appropriate restrictions

2. **Yelp Developer Account** (Optional, but recommended)
   - Sign up at [Yelp Fusion](https://www.yelp.com/developers)
   - Create a new app to get your API key
   - Used for finding restaurants when rest areas aren't available

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
   ```bash
   GOOGLE_MAPS_API_KEY=your_google_cloud_api_key
   YELP_API_KEY=your_yelp_fusion_api_key  # Optional
   ```

3. Validate your setup:
   ```bash
   python main.py
   ```
   You should see a test route from Baltimore to Nashville with suggested stops.

## API Reference

### MCP Tools

#### `plan_route_with_breaks`
Plans a route with strategic break points.

```python
plan_route_with_breaks(
    origin: str,                     # Starting location (e.g., "New York, NY")
    destination: str,                # Ending location (e.g., "Boston, MA")
    break_every_minutes: int = 120,  # Break interval (30-360 minutes)
    departure_time: str | None = None # ISO8601 datetime or None for now
) -> dict
```

**Returns:**
```json
{
    "origin": "New York, NY",
    "destination": "Boston, MA",
    "total_drive_time": "4 hours 15 mins",
    "recommended_breaks": [
        {
            "lat": 41.2345,
            "lng": -73.1234,
            "segment_minutes": 120.5
        }
    ]
}
```

#### `enrich_route`
Enhanced route planning with rest stops and weather information.

```python
enrich_route(
    origin: str,
    destination: str,
    break_every_minutes: int = 120,
    departure_time: str | None = None
) -> dict
```

**Returns:**
```json
{
    "origin": "New York, NY",
    "destination": "Boston, MA",
    "total_drive_time": "4 hours 15 mins",
    "stops": [
        {
            "type": "rest_area",  # or "restaurant"
            "name": "Service Plaza",
            "lat": 41.2345,
            "lng": -73.1234,
            "rating": 4.2,
            "address": "I-95 Mile Marker 45",
            "weather": "Partly Cloudy, 72°F"
        }
    ],
    "maps_url": "https://www.google.com/maps/dir/..."
}
```

### Error Handling

The API uses standard error responses:
```json
{
    "error": "No route found between locations",
    "status": "error",
    "service": "Google Maps",  # or "Yelp", "NWS"
    "status_code": 404
}
```

Common error scenarios:
- Invalid location format
- No route found between locations
- Location outside US (for weather)
- API key issues
- Rate limiting

> Note: Google Maps share URLs have a practical limit of 8 waypoints to ensure compatibility across devices and platforms.

## Advanced Usage

### Custom Break Intervals
```python
# Short breaks every hour
result = enrich_route("Seattle, WA", "Portland, OR", break_every_minutes=60)

# Longer breaks every 3 hours
result = enrich_route("Chicago, IL", "Denver, CO", break_every_minutes=180)
```

### Planned Departure Times
```python
# Plan a future trip
result = enrich_route(
    "Miami, FL",
    "Atlanta, GA",
    departure_time="2025-12-25T06:00:00"
)
```

### Error Handling
```python
result = enrich_route("New York, NY", "Los Angeles, CA")
if result.get("status") == "error":
    print(f"Error: {result['error']}")
    print(f"Service: {result.get('service')}")
    print(f"Status Code: {result.get('status_code')}")
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://github.com/anthropic-labs/mcp)
- Uses Google Maps Platform for routing and places
- Weather data provided by the US National Weather Service
- Restaurant data from Yelp Fusion API
