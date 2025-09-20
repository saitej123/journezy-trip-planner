import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch


load_dotenv()


def get_formatted_hotels_info(hotels: list, currency_code: str = "USD") -> str:
    # Ensure consistent currency symbol mapping
    currency_upper = currency_code.upper()
    if currency_upper == "USD":
        symbol = "$"
    elif currency_upper == "INR":
        symbol = "₹"
    else:
        symbol = "$"  # Default fallback
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
            # Clean and format price consistently
            try:
                # Remove any existing currency symbols and clean the price
                rate_clean = str(rate_per_night).replace("$", "").replace("₹", "").replace(",", "").strip()
                rate_float = float(rate_clean)
                rate_text = f"{symbol}{rate_float:,.0f}"
            except (ValueError, TypeError):
                # If conversion fails, use original text with proper symbol
                rate_text = str(rate_per_night)
                if not any(s in rate_text for s in ["$", "₹"]):
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
    
    # Create comprehensive search query based on requirements
    search_query = f"{city} hotels"
    
    # Add specific amenity requirements
    amenity_requirements = []
    if toddler_friendly and senior_friendly:
        amenity_requirements.extend([
            "family friendly", "accessible", "elevator access", 
            "kids amenities", "cribs available", "high chairs",
            "wheelchair accessible", "grab bars", "ground floor rooms"
        ])
    elif toddler_friendly:
        amenity_requirements.extend([
            "family friendly", "kids amenities", "cribs available", 
            "high chairs", "children's pool", "playground",
            "baby equipment", "stroller accessible"
        ])
    elif senior_friendly:
        amenity_requirements.extend([
            "accessible", "elevator access", "wheelchair accessible",
            "grab bars", "ground floor rooms", "senior friendly",
            "mobility assistance", "comfortable seating"
        ])
    
    if amenity_requirements:
        search_query += f" {' '.join(amenity_requirements[:5])}"  # Limit to avoid overly long queries
    
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
        print(f"🔍 [HOTELS] Search query: {search_query}")
        print(f"🔍 [HOTELS] Check-in: {check_in_date}, Check-out: {check_out_date}")
        
        # Primary search using google_hotels engine
        search = GoogleSearch(params)
        results = search.get_dict()
        
        print(f"🔍 [HOTELS] API Response keys: {list(results.keys()) if results else 'No response'}")
        
        if "error" in results:
            print(f"❌ [HOTELS] SerpAPI error: {results['error']}")
            raise ValueError(f"SerpAPI error: {results['error']}")
        
        hotels_data = results.get("properties", [])
        print(f"🔍 [HOTELS] Found {len(hotels_data)} hotels from primary search")
        
        # If limited results from google_hotels, try regular Google search
        if len(hotels_data) < 10:
            print("⚠️ [HOTELS] Limited results from google_hotels, trying regular Google search...")
            
            # Multiple alternative search strategies
            alternative_searches = [
                f"best hotels in {city}",
                f"top rated hotels {city}",
                f"luxury hotels {city}",
                f"budget hotels {city}",
                f"business hotels {city}",
                f"{city} accommodation booking"
            ]
            
            for alt_query in alternative_searches:
                try:
                    alt_params = {
                        "api_key": SERPAPI_KEY,
                        "engine": "google",
                        "q": alt_query,
                        "location": "Austin, Texas, United States",
                        "google_domain": "google.com",
                        "gl": "us",
                        "hl": "en",
                        "num": 20
                    }
                    
                    alt_search = GoogleSearch(alt_params)
                    alt_results = alt_search.get_dict()
                    
                    # Extract hotel information from organic results
                    if "organic_results" in alt_results:
                        for result in alt_results["organic_results"][:10]:
                            title = result.get("title", "")
                            # Filter for hotel-related results
                            if any(keyword in title.lower() for keyword in ["hotel", "resort", "inn", "lodge", "suites", "accommodation"]):
                                alt_hotel = {
                                    "name": title,
                                    "rate_per_night": "Check website for rates",
                                    "overall_rating": 4.0,  # Default rating
                                    "reviews": "Multiple reviews",
                                    "location_rating": "Good location",
                                    "amenities": ["WiFi", "Air Conditioning", "24/7 Reception"],
                                    "images": [{"thumbnail": result.get("thumbnail", "")}] if result.get("thumbnail") else []
                                }
                                
                                # Check if hotel already exists (avoid duplicates)
                                existing_names = {h.get("name", "").lower() for h in hotels_data}
                                if title.lower() not in existing_names:
                                    hotels_data.append(alt_hotel)
                    
                    # Extract from local_results if available
                    if "local_results" in alt_results:
                        for result in alt_results["local_results"][:5]:
                            if any(keyword in result.get("title", "").lower() for keyword in ["hotel", "resort", "inn", "lodge"]):
                                local_hotel = {
                                    "name": result.get("title", ""),
                                    "rate_per_night": "Contact for rates",
                                    "overall_rating": result.get("rating", 4.0),
                                    "reviews": f"{result.get('reviews', 'Multiple')} reviews",
                                    "location_rating": "Local area",
                                    "amenities": ["Local Services", "Easy Access"],
                                    "images": [{"thumbnail": result.get("thumbnail", "")}] if result.get("thumbnail") else []
                                }
                                
                                existing_names = {h.get("name", "").lower() for h in hotels_data}
                                if result.get("title", "").lower() not in existing_names:
                                    hotels_data.append(local_hotel)
                    
                    print(f"🔍 [HOTELS] Alternative search '{alt_query}' added hotels, total now: {len(hotels_data)}")
                    
                    # Stop if we have enough hotels
                    if len(hotels_data) >= 20:
                        break
                        
                except Exception as e:
                    print(f"⚠️ [HOTELS] Alternative search failed for '{alt_query}': {str(e)}")
                    continue
        
        print(f"🔍 [HOTELS] Total hotels before filtering: {len(hotels_data)}")
        
        # Enhanced filtering and sorting
        def _price(h: dict) -> float:
            p = None
            rp = h.get("rate_per_night")
            if isinstance(rp, dict):
                p = rp.get("lowest") or rp.get("exact") or rp.get("value")
            elif isinstance(rp, (int, float)):
                p = rp
            elif isinstance(rp, str):
                # Try to extract number from string
                import re
                numbers = re.findall(r'\d+', rp)
                if numbers:
                    p = float(numbers[0])
            if p is None:
                p = h.get("price") or h.get("lowest_price")
            try:
                return float(p) if p is not None else 999999  # High value for unknown prices
            except Exception:
                return 999999

        def _rating(h: dict) -> float:
            rating = h.get("overall_rating") or h.get("rating") or 3.5
            try:
                return float(rating)
            except:
                return 3.5

        # Sort by rating first, then by price
        hotels_data = sorted(hotels_data, key=lambda h: (-_rating(h), _price(h)))
        
        # Take a good mix of hotels
        high_rated = [h for h in hotels_data if _rating(h) >= 4.0][:8]  # Top rated
        budget_options = [h for h in hotels_data if h not in high_rated][:4]  # Budget options
        
        selected_hotels = high_rated + budget_options
        
        # Ensure we have at least some hotels
        if len(selected_hotels) < 8 and len(hotels_data) >= 8:
            selected_hotels = hotels_data[:8]
        elif len(selected_hotels) < len(hotels_data):
            # Fill remaining slots
            remaining = [h for h in hotels_data if h not in selected_hotels]
            selected_hotels.extend(remaining[:max(0, 12 - len(selected_hotels))])
        
        print(f"🔍 [HOTELS] Selected {len(selected_hotels)} hotels for display")
        
        first_line = f"Accommodations in {city}:"
        if toddler_friendly:
            first_line += " (family-friendly options included)"
        if senior_friendly:
            first_line += " (senior-friendly options included)"
            
        return first_line + "\n\n" + get_formatted_hotels_info(selected_hotels, currency_code=currency)
    except Exception as e:
        raise Exception(f"Failed to find hotels: {str(e)}")
