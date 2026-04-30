from typing import Iterable, Tuple
from urllib.parse import quote_plus

def build_maps_url(origin: str, destination: str, waypoints: Iterable[Tuple[float, float]]) -> str:
    """Build a Google Maps share URL with waypoints.
    Note: The URL supports a limited number of waypoints; we cap at 8 for reliability.
    """
    origin_q = quote_plus(origin)
    dest_q = quote_plus(destination)

    # Cap waypoints to avoid URL/Maps limits
    capped = list(waypoints)[:8]
    wp = "|".join([f"{lat},{lon}" for lat, lon in capped])

    url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin_q}"
        f"&destination={dest_q}"
        f"&waypoints={quote_plus(wp)}"
        f"&travelmode=driving"
    )
    return url
