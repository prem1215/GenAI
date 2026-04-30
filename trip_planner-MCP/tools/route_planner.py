import datetime
from typing import List, Tuple

def _extract_steps(directions) -> List[dict]:
    # Support multi-leg routes by flattening steps across legs
    steps = []
    for leg in directions[0].get("legs", []):
        steps.extend(leg.get("steps", []))
    return steps

def plan_route_with_breaks_core(gmaps_client, origin: str, destination: str, break_every_minutes: int, departure_time: datetime.datetime):
    """Core logic: compute traffic-aware breakpoints using Google Directions.
    Returns (breakpoints_list, total_time_text)
    """
    directions = gmaps_client.directions(
        origin,
        destination,
        mode="driving",
        departure_time=departure_time,
        traffic_model="best_guess"
    )
    if not directions:
        return [], "0 mins"

    # Prefer total duration_in_traffic if available
    legs = directions[0].get("legs", [])
    total_text = None
    for leg in legs:
        total_text = leg.get("duration_in_traffic", leg.get("duration", {})).get("text", total_text)

    steps = _extract_steps(directions)
    breaks = []
    elapsed = 0.0  # minutes

    for step in steps:
        dur_sec = step.get("duration_in_traffic", step.get("duration", {})).get("value")
        if dur_sec is None:
            continue
        elapsed += dur_sec / 60.0
        if elapsed >= break_every_minutes:
            eloc = step.get("end_location", {})
            lat, lng = eloc.get("lat"), eloc.get("lng")
            if lat is not None and lng is not None:
                breaks.append({"lat": lat, "lng": lng, "segment_minutes": round(elapsed, 1)})
            elapsed = 0.0

    return breaks, (total_text or "unknown")
