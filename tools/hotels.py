import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch


load_dotenv()


def get_formatted_hotels_info(hotels: list, currency_code: str = "USD") -> str:
    symbol = "$" if currency_code.upper() == "USD" else "₹"
    formatted_hotels = []
    for hotel in hotels:
        name = hotel.get("name", "Hotel")

        # Price extraction (robust to different shapes)
        rate_per_night = None
        rate_obj = hotel.get("rate_per_night")
        if isinstance(rate_obj, dict):
            rate_per_night = rate_obj.get("lowest") or rate_obj.get("exact") or rate_obj.get("value")
        elif isinstance(rate_obj, str):
            rate_per_night = rate_obj
        # Additional fallbacks seen in some responses
        if not rate_per_night:
            rate_plan = hotel.get("rate_plan") or {}
            rate_per_night = rate_plan.get("price") or rate_plan.get("rate")
        if not rate_per_night:
            rate_per_night = hotel.get("price") or hotel.get("lowest_price")

        overall_rating = hotel.get("overall_rating") or hotel.get("rating")
        reviews = hotel.get("reviews") or hotel.get("reviews_count") or ""
        location_rating = hotel.get("location_rating") or hotel.get("location_score")
        amenities_list = hotel.get("amenities") or []

        # Image fallback
        image_url = ""
        images = hotel.get("images") or []
        if images:
            first = images[0] or {}
            image_url = first.get("thumbnail") or first.get("original_image") or first.get("link") or ""

        formatted_hotels.append(name)
        if rate_per_night:
            # Ensure value comes formatted with currency symbol for consistency
            rate_text = str(rate_per_night)
            if not any(s in rate_text for s in ["$", "₹", "USD", "INR"]):
                rate_text = f"{symbol}{rate_text}"
            formatted_hotels.append(f"Rate per night: {rate_text}")
        else:
            formatted_hotels.append("Rate per night: N/A")
        if overall_rating:
            formatted_hotels.append(f"Rating: {overall_rating} ({reviews})")
        if location_rating:
            formatted_hotels.append(f"Location Rating: {location_rating}")
        if amenities_list:
            formatted_hotels.append(f"Amenities: {', '.join(amenities_list[:7])}")
        formatted_hotels.append(f"Image: {image_url if image_url else 'N/A'}")
        formatted_hotels.append("")
    return "\n".join(formatted_hotels)


def find_hotels(
    city: str = Field(..., description="The city where the hotels are located"),
    check_in_date: str = Field(
        ..., description="The check-in date in the format YYYY-MM-DD"
    ),
    check_out_date: str = Field(
        None, description="The check-out date in the format YYYY-MM-DD"
    ),
    currency: str = "USD",
    toddler_friendly: bool = False,
    senior_friendly: bool = False,
) -> str:
    """
    Find hotels in a specific city with optional toddler and senior-friendly considerations.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    
    # Modify search query based on requirements
    search_query = city
    if toddler_friendly and senior_friendly:
        search_query += " family friendly accessible hotels"
    elif toddler_friendly:
        search_query += " family friendly hotels with kids amenities"
    elif senior_friendly:
        search_query += " accessible hotels senior friendly"
    
    params = {
        "engine": "google_hotels",
        "q": search_query,
        "hl": "en",
        "gl": "us",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": currency,
        "api_key": SERPAPI_KEY,
    }

    try:
        print(f"\n> Finding hotels in {city}\n")
        search = GoogleSearch(params)
        results = search.get_dict()
        print(results)
        if "error" in results:
            raise ValueError(f"SerpAPI error: {results['error']}")
        hotels_data = results.get("properties", [])
        # Filter 4.0+ rating and take cheapest 3 by detected price when possible
        def _price(h: dict) -> float:
            p = None
            rp = h.get("rate_per_night")
            if isinstance(rp, dict):
                p = rp.get("lowest") or rp.get("exact") or rp.get("value")
            elif isinstance(rp, (int, float)):
                p = rp
            if p is None:
                p = h.get("price") or h.get("lowest_price")
            try:
                return float(p)
            except Exception:
                return float("inf")

        # Prefer cheapest overall (not just top-5), then filter by 4.0+ to keep quality
        hotels_sorted = sorted(hotels_data, key=_price)
        cheap_first = hotels_sorted[:15]  # look at more candidates first
        rated = [h for h in cheap_first if (h.get("overall_rating") or h.get("rating") or 0) >= 4.0]
        # Keep up to 6 hotels, favouring cheapest 4+ star; if too few, backfill with next cheapest
        selected = rated[:6]
        if len(selected) < 6:
            backfill = [h for h in cheap_first if h not in selected]
            selected.extend(backfill[: (6 - len(selected))])
        hotels_data = selected
        first_line = f"Accommodations in {city}:"
        return first_line + "\n\n" + get_formatted_hotels_info(hotels_data[:5], currency_code=currency)
    except Exception as e:
        raise Exception(f"Failed to find hotels: {str(e)}")
