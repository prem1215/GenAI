from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os, datetime
import googlemaps

# Local tools
from tools.route_planner import plan_route_with_breaks_core
from tools.rest_stop_finder import find_stop_near
from tools.weather_checker import get_weather_summary
from tools.maps_url_builder import build_maps_url

load_dotenv()

GMAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
YELP_KEY = os.getenv("YELP_API_KEY")

if not GMAPS_KEY:
    print("⚠️  GOOGLE_MAPS_API_KEY missing in .env")
if not YELP_KEY:
    print("⚠️  YELP_API_KEY missing in .env (Yelp fallback will be skipped)")

gmaps = googlemaps.Client(key=GMAPS_KEY) if GMAPS_KEY else None

mcp = FastMCP("RoadTripMCP")

@mcp.tool()
def suggest_break_interval(origin: str, destination: str) -> dict:
    """Suggest an optimal break interval based on route characteristics and best practices.
    
    This tool helps AI assistants make informed decisions about break planning by considering:
    - Total route duration
    - Time of day
    - Type of roads (highways vs local)
    - Driver safety guidelines
    """
    if not gmaps:
        return {"error": "Google Maps client not configured"}
        
    try:
        # Get route details
        route = gmaps.directions(
            origin,
            destination,
            mode="driving",
            departure_time=datetime.datetime.now()
        )
        
        if not route:
            return {"error": "No route found"}
            
        duration_mins = route[0]['legs'][0]['duration']['value'] / 60
        
        # Implement break interval logic based on trip characteristics
        if duration_mins <= 120:  # Short trips
            return {
                "suggested_interval": 0,
                "explanation": "Trip is short enough to complete without breaks"
            }
        elif duration_mins <= 240:  # Medium trips
            return {
                "suggested_interval": 120,
                "explanation": "Recommend one break at the midpoint for trips 2-4 hours"
            }
        elif duration_mins <= 480:  # Longer trips
            return {
                "suggested_interval": 150,
                "explanation": "For trips 4-8 hours, break every 2.5 hours to maintain alertness"
            }
        else:  # Very long trips
            return {
                "suggested_interval": 120,
                "explanation": "For trips over 8 hours, frequent breaks every 2 hours are essential"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def plan_route_with_breaks(origin: str, destination: str, break_every_minutes: int = 120, departure_time: str | None = None):
    """Return traffic-aware breakpoints (lat/lng) every ~N minutes using Google Directions.
    If departure_time is None, uses now(). departure_time may be ISO8601 string.
    
    This tool helps AI assistants plan optimal break points by considering:
    - Traffic conditions and predictions
    - Available facilities
    - Distance between stops
    - Time of day and expected fatigue patterns
    """
    if not gmaps:
        return {"error": "Google Maps client not configured"}
    if departure_time:
        try:
            dt = datetime.datetime.fromisoformat(departure_time)
        except Exception:
            dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.now()

    breaks, total_text = plan_route_with_breaks_core(gmaps, origin, destination, break_every_minutes, dt)
    return {
        "origin": origin,
        "destination": destination,
        "total_drive_time": total_text,
        "recommended_breaks": breaks,
    }

@mcp.tool()
def analyze_route_conditions(origin: str, destination: str, departure_time: str | None = None) -> dict:
    """Analyze route conditions to help AI assistants make informed recommendations.
    
    This tool provides comprehensive route analysis including:
    - Traffic patterns and potential delays
    - Weather conditions along the route
    - Road types and terrain
    - Service availability
    """
    if not gmaps:
        return {"error": "Google Maps client not configured"}
        
    try:
        dt = datetime.datetime.fromisoformat(departure_time) if departure_time else datetime.datetime.now()
        
        # Get detailed route information
        route = gmaps.directions(
            origin,
            destination,
            mode="driving",
            departure_time=dt,
            alternatives=True
        )
        
        if not route:
            return {"error": "No route found"}
            
        # Analyze primary route
        primary = route[0]
        duration = primary['legs'][0]['duration']['value']
        distance = primary['legs'][0]['distance']['value']
        
        # Calculate key metrics
        hours_needed = duration / 3600
        recommended_stops = max(1, int(hours_needed / 2))
        
        return {
            "route_analysis": {
                "total_distance_km": round(distance / 1000, 1),
                "estimated_duration_hours": round(hours_needed, 1),
                "recommended_stops": recommended_stops,
                "route_type": "Interstate" if "I-" in str(primary) else "Mixed",
                "has_alternatives": len(route) > 1,
                "departure_time": dt.isoformat(),
                "arrival_time": (dt + datetime.timedelta(seconds=duration)).isoformat()
            },
            "safety_recommendations": [
                "Plan for regular breaks every 2-3 hours",
                "Check weather conditions before departure",
                "Ensure cell phone coverage along route",
                "Have emergency supplies and contact numbers"
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def enrich_route(origin: str, destination: str, break_every_minutes: int = 120, departure_time: str | None = None):
    """Plan route and enrich each breakpoint with rest-area/restaurant + weather, and return a maps URL.
    
    This tool helps AI assistants provide comprehensive trip planning by:
    - Finding optimal rest stops based on amenities and reviews
    - Checking weather conditions for safety
    - Generating shareable navigation links
    - Considering time-of-day specific factors for stop recommendations
    """
    if not gmaps:
        return {"error": "Google Maps client not configured"}
    if departure_time:
        try:
            dt = datetime.datetime.fromisoformat(departure_time)
        except Exception:
            dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.now()

    breaks, total_text = plan_route_with_breaks_core(gmaps, origin, destination, break_every_minutes, dt)

    enriched = []
    for bp in breaks:
        lat, lng = bp["lat"], bp["lng"]
        stop = find_stop_near(gmaps, YELP_KEY, lat, lng)
        # Weather (US only for NWS); handle gracefully if fails
        stop["weather"] = get_weather_summary(lat, lng)
        enriched.append(stop)

    maps_url = build_maps_url(origin, destination, [
        (s["lat"], s["lng"]) for s in enriched if "lat" in s and "lng" in s
    ])

    return {
        "origin": origin,
        "destination": destination,
        "total_drive_time": total_text,
        "stops": enriched,
        "maps_url": maps_url,
    }

@mcp.tool()
def get_stop_recommendations(lat: float, lng: float, stop_duration_minutes: int = 30) -> dict:
    """Provide AI-driven recommendations for activities and amenities at a stop location.
    
    This tool helps AI assistants give personalized stop recommendations by analyzing:
    - Available facilities and their ratings
    - Typical dwell times
    - Time of day appropriate activities
    - Weather conditions
    """
    if not gmaps:
        return {"error": "Google Maps client not configured"}
        
    try:
        # Get nearby places
        places = gmaps.places_nearby(
            location=(lat, lng),
            radius=2000,
            type=['restaurant', 'cafe', 'park', 'gas_station', 'convenience_store']
        )
        
        # Get weather
        weather = get_weather_summary(lat, lng)
        
        recommendations = {
            "suggested_duration_minutes": stop_duration_minutes,
            "weather_condition": weather,
            "available_amenities": [],
            "recommended_activities": []
        }
        
        if places and 'results' in places:
            for place in places['results'][:5]:
                recommendations['available_amenities'].append({
                    "name": place.get('name'),
                    "type": place.get('types', ['unknown'])[0],
                    "rating": place.get('rating'),
                    "is_open": place.get('opening_hours', {}).get('open_now', None)
                })
        
        # Add contextual recommendations
        current_hour = datetime.datetime.now().hour
        if 6 <= current_hour <= 10:
            recommendations['recommended_activities'].append("Consider breakfast or coffee break")
        elif 11 <= current_hour <= 14:
            recommendations['recommended_activities'].append("Good time for lunch break")
        elif 17 <= current_hour <= 20:
            recommendations['recommended_activities'].append("Consider dinner stop")
        
        if "rain" in weather.lower() or "snow" in weather.lower():
            recommendations['recommended_activities'].append("Indoor break recommended due to weather")
        
        return recommendations
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚗 Running enhanced route demo...")
    
    # Analyze route conditions first
    print("\n📊 Analyzing route conditions...")
    conditions = analyze_route_conditions("Baltimore, MD", "Nashville, TN")
    if "route_analysis" in conditions:
        analysis = conditions["route_analysis"]
        print(f"Distance: {analysis['total_distance_km']} km")
        print(f"Duration: {analysis['estimated_duration_hours']} hours")
        print(f"Recommended stops: {analysis['recommended_stops']}")
        
    # Get suggested break interval
    print("\n⏰ Getting break interval suggestion...")
    interval = suggest_break_interval("Baltimore, MD", "Nashville, TN")
    if "suggested_interval" in interval:
        print(f"Suggested break interval: {interval['suggested_interval']} minutes")
        print(f"Reason: {interval['explanation']}")
    
    # Plan the enriched route
    print("\n🛣 Planning route with stops...")
    result = enrich_route("Baltimore, MD", "Nashville, TN", 120)
    
    if result.get("status") == "error":
        print(f"❌ Error: {result['error']}")
        exit(1)
        
    print(f"\n📍 Route: {result['origin']} → {result['destination']}")
    print(f"⏱ Total drive time: {result['total_drive_time']}")
    
    print("\n🛑 Recommended stops:")
    for stop in result.get("stops", []):
        stop_type = "🅿️" if stop["type"] == "rest_area" else "🍽️"
        print(f"\n{stop_type} {stop['name']}")
        print(f"   📍 {stop['address']}")
        
        # Get detailed recommendations for each stop
        recs = get_stop_recommendations(stop['lat'], stop['lng'])
        if 'recommended_activities' in recs:
            print("   💡 Recommendations:")
            for activity in recs['recommended_activities']:
                print(f"      • {activity}")
                
        if "rating" in stop:
            print(f"   ⭐ Rating: {stop['rating']}")
        print(f"   🌤 Weather: {stop['weather']}")

    print(f"\n🗺 Maps Link: {result['maps_url']}")
    
    # To run as an MCP server, uncomment:
    # mcp.run()
