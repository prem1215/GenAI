import requests

def find_stop_near(gmaps_client, yelp_key: str | None, lat: float, lon: float, radius: int = 15000) -> dict:
    """Prefer state/public rest areas near (lat, lon) using Google Places; else Yelp restaurants.
    Returns a dict with at least: type, name, lat, lng, address, rating (optional), url (optional)
    """
    # 1) Try Google Places 'rest_area'
    try:
        rest = gmaps_client.places_nearby(location=(lat, lon), radius=radius, type='rest_area')
        results = rest.get("results", [])
        if results:
            top = results[0]
            loc = top.get("geometry", {}).get("location", {})
            return {
                "type": "rest_area",
                "name": top.get("name"),
                "lat": loc.get("lat", lat),
                "lng": loc.get("lng", lon),
                "rating": top.get("rating"),
                "address": top.get("vicinity"),
                "source": "google_places"
            }
    except Exception:
        # continue to Yelp fallback
        pass

    # 2) Yelp fallback (restaurants)
    if not yelp_key:
        return {
            "type": "none",
            "message": "No rest area found nearby and Yelp key not configured",
            "lat": lat, "lng": lon
        }

    try:
        headers = {"Authorization": f"Bearer {yelp_key}"}
        params = {
            "latitude": lat,
            "longitude": lon,
            "categories": "restaurants",
            "sort_by": "rating",
            "limit": 3
        }
        r = requests.get("https://api.yelp.com/v3/businesses/search", headers=headers, params=params, timeout=12)
        data = r.json().get("businesses", [])
        if data:
            top = data[0]
            disp_addr = " ".join(top.get("location", {}).get("display_address", []))
            coords = top.get("coordinates", {})
            return {
                "type": "restaurant",
                "name": top.get("name"),
                "rating": top.get("rating"),
                "review_count": top.get("review_count"),
                "address": disp_addr,
                "url": top.get("url"),
                "lat": coords.get("latitude", lat),
                "lng": coords.get("longitude", lon),
                "source": "yelp"
            }
    except Exception:
        pass

    # 3) Nothing suitable
    return {"type": "none", "message": "No suitable stop nearby", "lat": lat, "lng": lon}
