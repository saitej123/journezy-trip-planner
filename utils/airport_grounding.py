"""
Airport Grounding Service
Uses Google's Gemini Grounding to find airports near cities that aren't in the database
"""
import google.generativeai as genai
import os
from typing import Optional, Dict, List
import json
import re

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)


def find_nearby_airport_with_grounding(city_name: str) -> Optional[Dict]:
    """
    Use Gemini with grounding to find the nearest airport to a city
    Returns airport information including code, name, and city
    """
    if not API_KEY:
        print("❌ [AIRPORT-GROUNDING] No Google API key found")
        return None
    
    try:
        print(f"🌐 [AIRPORT-GROUNDING] Searching for airport near '{city_name}' using Gemini grounding...")
        
        # Use Gemini to find airport information with grounding
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
What is the nearest commercial airport to {city_name}? 
Provide the response ONLY in this exact JSON format (no other text):
{{
    "airport_code": "3-letter IATA code",
    "airport_name": "full airport name",
    "city": "airport city name",
    "country": "country name",
    "distance_km": approximate distance in kilometers as a number
}}

If {city_name} has its own airport, use that. Otherwise, find the nearest major commercial airport.
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for factual responses
            ),
            tools='google_search_retrieval'  # Enable grounding
        )
        
        result_text = response.text.strip()
        print(f"🌐 [AIRPORT-GROUNDING] Gemini response: {result_text[:200]}...")
        
        # Try to extract JSON from the response
        # Remove markdown code blocks if present
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*$', '', result_text)
        result_text = result_text.strip()
        
        # Parse JSON
        try:
            airport_data = json.loads(result_text)
            
            # Validate the response
            if not airport_data.get('airport_code') or len(airport_data.get('airport_code', '')) != 3:
                print(f"⚠️ [AIRPORT-GROUNDING] Invalid airport code in response")
                return None
            
            result = {
                'code': airport_data['airport_code'].upper(),
                'name': airport_data['airport_name'],
                'city': airport_data['city'],
                'country': airport_data.get('country', 'Unknown'),
                'country_code': 'IN' if 'india' in airport_data.get('country', '').lower() else 'XX',
                'source': 'grounding',
                'distance_km': airport_data.get('distance_km', 0)
            }
            
            print(f"✅ [AIRPORT-GROUNDING] Found: {result['code']} - {result['name']} ({result['city']}) - {result['distance_km']}km away")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ [AIRPORT-GROUNDING] Failed to parse JSON response: {e}")
            print(f"   Raw response: {result_text}")
            
            # Fallback: try to extract airport code manually
            code_match = re.search(r'\b([A-Z]{3})\b', result_text)
            if code_match:
                code = code_match.group(1)
                print(f"⚠️ [AIRPORT-GROUNDING] Extracted airport code from text: {code}")
                return {
                    'code': code,
                    'name': f"Airport near {city_name}",
                    'city': city_name,
                    'country': 'Unknown',
                    'country_code': 'XX',
                    'source': 'grounding-fallback'
                }
            
            return None
    
    except Exception as e:
        print(f"❌ [AIRPORT-GROUNDING] Error: {str(e)}")
        return None


def enrich_airports_with_grounding(search_term: str, existing_airports: List[Dict]) -> List[Dict]:
    """
    If existing airport search returns no results, use grounding to find nearby airport
    Returns the enriched list of airports
    """
    # If we already have results, return them
    if existing_airports and len(existing_airports) > 0:
        return existing_airports
    
    # If no results and search term provided, try grounding
    if not search_term or len(search_term) < 2:
        return existing_airports
    
    print(f"🔍 [AIRPORT-GROUNDING] No results for '{search_term}', trying grounding service...")
    
    # Use grounding to find nearby airport
    grounded_airport = find_nearby_airport_with_grounding(search_term)
    
    if grounded_airport:
        # Format it like a database result
        result = {
            'code': grounded_airport['code'],
            'name': f"{grounded_airport['name']} (nearest to {search_term})",
            'city': grounded_airport['city'],
            'country': grounded_airport['country'],
            'country_code': grounded_airport['country_code'],
        }
        print(f"✅ [AIRPORT-GROUNDING] Returning grounded result: {result}")
        return [result]
    
    return existing_airports


def get_airport_suggestions_for_city(city_name: str) -> List[str]:
    """
    Get airport code suggestions for a city using grounding
    Useful for autocomplete/suggestions
    """
    airport = find_nearby_airport_with_grounding(city_name)
    if airport:
        return [airport['code']]
    return []

