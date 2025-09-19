import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def get_formatted_places_info(sights: list) -> str:
    formatted_places = []
    for sight in sights:
        formatted_places.append(sight["title"])
        formatted_places.append(f"Description: {sight.get('description', 'N/A')}")
        if "rating" in sight:
            formatted_places.append(f"Rating: {sight['rating']} ({sight['reviews']})")
        formatted_places.append(f"Price: {sight.get('price', 'N/A')}")
        formatted_places.append(f"Image: {sight.get('thumbnail', 'N/A')}")
        formatted_places.append("")
    return "\n".join(formatted_places)


def find_places_to_visit(
    location: str = Field(..., description="The location to find places to visit."),
    toddler_friendly: bool = False,
    senior_friendly: bool = False,
) -> str:
    """
    Find places to visit in a specific city with optional toddler and senior-friendly considerations.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    
    # Base search query
    base_query = f"top sights in {location}"
    
    # Add specific considerations
    if toddler_friendly and senior_friendly:
        base_query += " family friendly accessible attractions"
    elif toddler_friendly:
        base_query += " toddler friendly attractions playgrounds"
    elif senior_friendly:
        base_query += " senior friendly accessible attractions"
    
    params = {
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "q": base_query,
        "location": "Austin, Texas, United States",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
    }

    try:
        print(f"\n> Finding places to visit in {location}\n")
        print(f"🔍 [PLACES] Search query: {base_query}")
        print(f"🔍 [PLACES] API Key present: {bool(SERPAPI_KEY)}")
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        print(f"🔍 [PLACES] API Response keys: {list(results.keys()) if results else 'No response'}")
        
        if "error" in results:
            print(f"❌ [PLACES] SerpAPI error: {results['error']}")
            raise ValueError(f"SerpAPI error: {results['error']}")

        places_data = results.get("top_sights", {"sights": []}).get("sights", [])
        print(f"🔍 [PLACES] Found {len(places_data)} places")
        
        if not places_data:
            print("⚠️ [PLACES] No places found, trying alternative search...")
            # Try alternative search without location restriction
            alt_params = {
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": f"tourist attractions {location}",
                "google_domain": "google.com",
                "gl": "us",
                "hl": "en",
            }
            alt_search = GoogleSearch(alt_params)
            alt_results = alt_search.get_dict()
            places_data = alt_results.get("top_sights", {"sights": []}).get("sights", [])
            print(f"🔍 [PLACES] Alternative search found {len(places_data)} places")

        first_line = f"Here are the top places to visit in {location}:"
        if toddler_friendly:
            first_line += " (toddler-friendly options included)"
        if senior_friendly:
            first_line += " (senior-friendly options included)"
        
        formatted_result = first_line + "\n\n" + get_formatted_places_info(places_data)
        print(f"✅ [PLACES] Formatted result length: {len(formatted_result)}")
        return formatted_result
    except Exception as e:
        print(f"❌ [PLACES] Error: {str(e)}")
        import traceback
        print(f"❌ [PLACES] Traceback: {traceback.format_exc()}")
        raise Exception(f"Failed to find places: {str(e)}")
