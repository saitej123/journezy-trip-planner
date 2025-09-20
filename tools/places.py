import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def get_formatted_places_info(sights: list) -> str:
    if not sights or not isinstance(sights, list):
        print("⚠️ [PLACES-FORMAT] No sights provided to format or invalid type")
        return "No places found."
    
    formatted_places = []
    for i, sight in enumerate(sights):
        try:
            if not isinstance(sight, dict):
                print(f"⚠️ [PLACES-FORMAT] Sight {i+1} is not a dictionary, skipping: {sight}")
                continue
                
            print(f"🔍 [PLACES-FORMAT] Processing sight {i+1}: {sight.get('title', 'Unknown')}")
            print(f"🔍 [PLACES-FORMAT] Available keys: {list(sight.keys())}")
            
            # Place name
            title = sight.get("title", "Unknown Place")
            if not title or title.strip() == "":
                title = "Unknown Place"
            formatted_places.append(title)
            
            # Description
            description = sight.get('description', sight.get('snippet', 'N/A'))
            if not description or description.strip() == "":
                description = "No description available"
            formatted_places.append(f"Description: {description}")
            
            # Rating and reviews
            rating = sight.get('rating')
            if rating and str(rating).replace('.', '').isdigit():
                reviews = sight.get('reviews', '0 reviews')
                if not isinstance(reviews, str):
                    reviews = f"{reviews} reviews" if reviews else "0 reviews"
                formatted_places.append(f"Rating: {rating} ({reviews})")
            else:
                formatted_places.append("Rating: N/A")
            
            # Price
            price = sight.get('price', sight.get('admission_fee', 'Free Entry'))
            if not price or str(price).strip() == "":
                price = "Free Entry"
            formatted_places.append(f"Price: {price}")
            
            # Image - check multiple possible image fields with proper validation
            image_url = None
            for img_field in ['thumbnail', 'image', 'photo', 'picture']:
                if img_field in sight and sight[img_field]:
                    potential_url = sight[img_field]
                    # Validate that it's a proper URL
                    if isinstance(potential_url, str) and (potential_url.startswith('http') or potential_url.startswith('//')):
                        image_url = potential_url
                        break
            
            if image_url:
                print(f"🖼️ [PLACES-FORMAT] Found valid image URL: {image_url}")
                formatted_places.append(f"Image: {image_url}")
            else:
                print(f"⚠️ [PLACES-FORMAT] No valid image found for {sight.get('title', 'Unknown')}")
                # Provide a placeholder or fallback image
                formatted_places.append("Image: https://via.placeholder.com/300x200?text=No+Image+Available")
            
            formatted_places.append("")
            
        except Exception as e:
            print(f"❌ [PLACES-FORMAT] Error processing sight {i+1}: {str(e)}")
            # Add a minimal entry for failed sights
            formatted_places.extend([
                f"Place {i+1}",
                "Description: Error loading details",
                "Rating: N/A",
                "Price: N/A",
                "Image: https://via.placeholder.com/300x200?text=No+Image+Available",
                ""
            ])
    
    result = "\n".join(formatted_places)
    print(f"✅ [PLACES-FORMAT] Formatted {len(sights)} places, result length: {len(result)}")
    return result


def find_places_to_visit(
    location: str = Field(..., description="The location to find places to visit."),
    toddler_friendly: bool = False,
    senior_friendly: bool = False,
) -> str:
    """
    Find places to visit in a specific city with optional toddler and senior-friendly considerations.
    """
    
    # Input validation
    if not location or not isinstance(location, str) or location.strip() == "":
        print("❌ [PLACES] Invalid location provided")
        return "Error: Invalid location provided."

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        print("❌ [PLACES] No SerpAPI key found")
        return "Error: API configuration missing."
    
    # Clean and normalize location
    location = location.strip()
    
    # Create comprehensive search query based on traveler needs
    base_query = f"best attractions and places to visit in {location}"
    
    # Add specific traveler requirements for more targeted results
    if toddler_friendly and senior_friendly:
        base_query += " family friendly accessible multi-generational attractions stroller wheelchair"
    elif toddler_friendly:
        base_query += " family kids children toddler friendly attractions playgrounds interactive exhibits"
    elif senior_friendly:
        base_query += " senior accessible wheelchair friendly attractions museums cultural sites easy walking"
    
    params = {
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "q": base_query,
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
        
        # Handle API errors
        if not results or not isinstance(results, dict):
            print("❌ [PLACES] No valid response from SerpAPI")
            raise ValueError("No valid response from SerpAPI")
            
        if "error" in results:
            print(f"❌ [PLACES] SerpAPI error: {results['error']}")
            raise ValueError(f"SerpAPI error: {results['error']}")

        # Try multiple data sources from SerpAPI response
        places_data = []
        
        # Primary source: top_sights
        if "top_sights" in results and "sights" in results["top_sights"]:
            primary_places = results["top_sights"]["sights"]
            if primary_places and isinstance(primary_places, list):
                places_data.extend(primary_places)
                print(f"🔍 [PLACES] Found {len(primary_places)} places from top_sights")
            else:
                print("⚠️ [PLACES] top_sights.sights is empty or invalid")
        else:
            print("⚠️ [PLACES] No top_sights found in API response")
        
        # Secondary source: organic_results (regular search results)
        if "organic_results" in results and results["organic_results"] is not None:
            organic_places = []
            organic_results = results["organic_results"]
            
            # Safely handle the organic results with proper validation
            if isinstance(organic_results, list) and len(organic_results) > 0:
                max_results = min(10, len(organic_results))
                for i in range(max_results):
                    try:
                        result = organic_results[i]
                        if not result or not isinstance(result, dict):
                            print(f"⚠️ [PLACES] Skipping invalid organic result at index {i}: {type(result)}")
                            continue
                            
                        title = result.get("title", "")
                        if title and any(keyword in title.lower() for keyword in ["attraction", "museum", "park", "tour", "visit", "see", "landmark"]):
                            organic_place = {
                                "title": title,
                                "description": result.get("snippet", ""),
                                "thumbnail": result.get("thumbnail", ""),
                                "rating": None,
                                "reviews": "0 reviews",
                                "price": "Check website"
                            }
                            organic_places.append(organic_place)
                    except (IndexError, KeyError, TypeError) as e:
                        print(f"⚠️ [PLACES] Error processing organic result at index {i}: {str(e)}")
                        continue
                
                places_data.extend(organic_places)
                print(f"🔍 [PLACES] Found {len(organic_places)} additional places from organic results")
            else:
                print("⚠️ [PLACES] organic_results is empty or not a valid list")
        else:
            print("⚠️ [PLACES] No organic_results found in API response")
        
        # Third source: local_results
        if "local_results" in results and results["local_results"] is not None:
            local_places = []
            local_results = results["local_results"]
            
            # Safely handle the local results with proper validation
            if isinstance(local_results, list) and len(local_results) > 0:
                max_results = min(10, len(local_results))
                for i in range(max_results):
                    try:
                        result = local_results[i]
                        if not result or not isinstance(result, dict):
                            print(f"⚠️ [PLACES] Skipping invalid local result at index {i}: {type(result)}")
                            continue
                            
                        local_place = {
                            "title": result.get("title", ""),
                            "description": result.get("type", "Local attraction"),
                            "thumbnail": result.get("thumbnail", ""),
                            "rating": result.get("rating", None),
                            "reviews": f"{result.get('reviews', 0)} reviews",
                            "price": "Contact for pricing"
                        }
                        local_places.append(local_place)
                    except (IndexError, KeyError, TypeError) as e:
                        print(f"⚠️ [PLACES] Error processing local result at index {i}: {str(e)}")
                        continue
                
                places_data.extend(local_places)
                print(f"🔍 [PLACES] Found {len(local_places)} places from local results")
            else:
                print("⚠️ [PLACES] local_results is empty or not a valid list")
        else:
            print("⚠️ [PLACES] No local_results found in API response")
        
        print(f"🔍 [PLACES] Total places found: {len(places_data)}")
        
        # If still limited results, try multiple alternative searches
        if len(places_data) < 5:
            print("⚠️ [PLACES] Limited results, trying multiple alternative searches...")
            
            alternative_queries = [
                f"tourist attractions {location}",
                f"things to do in {location}",
                f"must visit places {location}",
                f"best attractions {location}",
                f"{location} sightseeing spots",
                f"{location} landmarks museums parks"
            ]
            
            for alt_query in alternative_queries:
                try:
                    alt_params = {
                        "api_key": SERPAPI_KEY,
                        "engine": "google",
                        "q": alt_query,
                        "google_domain": "google.com",
                        "gl": "us",
                        "hl": "en",
                        "num": 20  # Request more results
                    }
                    alt_search = GoogleSearch(alt_params)
                    alt_results = alt_search.get_dict()
                    
                    # Check if alternative search returned valid results
                    if not alt_results or not isinstance(alt_results, dict):
                        print(f"⚠️ [PLACES] Alternative search '{alt_query}' returned no valid results")
                        continue
                        
                    if "error" in alt_results:
                        print(f"⚠️ [PLACES] Alternative search '{alt_query}' returned error: {alt_results['error']}")
                        continue
                    
                    # Extract from multiple sources in alternative search
                    alt_places = []
                    
                    # From top_sights
                    if "top_sights" in alt_results and "sights" in alt_results["top_sights"]:
                        top_sights = alt_results["top_sights"]["sights"]
                        if top_sights and isinstance(top_sights, list):
                            alt_places.extend(top_sights)
                    
                    # From organic results
                    if "organic_results" in alt_results and alt_results["organic_results"] is not None:
                        organic_results = alt_results["organic_results"]
                        
                        if isinstance(organic_results, list) and len(organic_results) > 0:
                            max_results = min(8, len(organic_results))
                            
                            for i in range(max_results):
                                try:
                                    result = organic_results[i]
                                    if not result or not isinstance(result, dict):
                                        continue
                                        
                                    alt_place = {
                                        "title": result.get("title", ""),
                                        "description": result.get("snippet", ""),
                                        "thumbnail": result.get("thumbnail", ""),
                                        "rating": None,
                                        "reviews": "0 reviews",
                                        "price": "Varies"
                                    }
                                    alt_places.append(alt_place)
                                except (IndexError, KeyError, TypeError) as e:
                                    print(f"⚠️ [PLACES] Error processing alt organic result at index {i}: {str(e)}")
                                    continue
                    
                    # Remove duplicates based on title
                    existing_titles = {place.get("title", "").lower() for place in places_data}
                    new_places = [place for place in alt_places if place.get("title", "").lower() not in existing_titles]
                    
                    places_data.extend(new_places)
                    print(f"🔍 [PLACES] Alternative query '{alt_query}' found {len(new_places)} new places")
                    
                    # Stop if we have enough places
                    if len(places_data) >= 15:
                        break
                        
                except Exception as e:
                    print(f"⚠️ [PLACES] Alternative search failed for '{alt_query}': {str(e)}")
                    continue
            
            print(f"🔍 [PLACES] Final total after alternative searches: {len(places_data)}")

        # If still no places found, create fallback places
        if len(places_data) == 0:
            print("⚠️ [PLACES] No places found from any source, creating comprehensive fallback recommendations")
            fallback_places = [
                {
                    "title": f"{location} City Center",
                    "description": "Explore the heart of the city with shops, restaurants, and local culture. Perfect for walking and discovering local life.",
                    "rating": "4.2",
                    "reviews": "Popular destination",
                    "price": "Free Entry",
                    "thumbnail": "https://via.placeholder.com/300x200?text=City+Center"
                },
                {
                    "title": f"{location} Historic District",
                    "description": "Discover the historical significance and beautiful architecture that tells the story of this destination.",
                    "rating": "4.3",
                    "reviews": "Historical significance",
                    "price": "Free Entry",
                    "thumbnail": "https://via.placeholder.com/300x200?text=Historic+District"
                },
                {
                    "title": f"{location} Local Markets",
                    "description": "Experience authentic local culture, traditional food, and artisan crafts at bustling local markets.",
                    "rating": "4.1",
                    "reviews": "Authentic experience",
                    "price": "Varies",
                    "thumbnail": "https://via.placeholder.com/300x200?text=Local+Markets"
                },
                {
                    "title": f"{location} Parks & Gardens",
                    "description": "Relax and enjoy nature in beautiful parks and gardens, perfect for families and peaceful moments.",
                    "rating": "4.4",
                    "reviews": "Nature lovers",
                    "price": "Free Entry",
                    "thumbnail": "https://via.placeholder.com/300x200?text=Parks+%26+Gardens"
                },
                {
                    "title": f"{location} Cultural Attractions",
                    "description": "Immerse yourself in local culture through museums, galleries, and cultural centers.",
                    "rating": "4.0",
                    "reviews": "Cultural experience",
                    "price": "Entry fees vary",
                    "thumbnail": "https://via.placeholder.com/300x200?text=Cultural+Attractions"
                }
            ]
            places_data = fallback_places
            print(f"🔍 [PLACES] Created {len(fallback_places)} comprehensive fallback places")

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
