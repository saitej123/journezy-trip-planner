from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

import google.generativeai as genai
import os
import json

from grounding_service import GroundedTourExtractor
import asyncio

class TourInfo(BaseModel):
    airport_from: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the primary departure airport e.g. LHR, LAX etc.",
    )
    alternative_airports_from: list[str] = Field(
        default_factory=list,
        description="List of alternative departure airport IATA codes, sorted by proximity",
    )
    airport_to: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the primary destination airport e.g. LHR, LAX etc.",
    )
    alternative_airports_to: list[str] = Field(
        default_factory=list,
        description="List of alternative destination airport IATA codes, sorted by proximity",
    )
    departure_date: str = Field(
        ..., description="The departure date in the format YYYY-MM-DD"
    )
    return_date: str = Field(
        ..., description="The return date in the format YYYY-MM-DD"
    )
    destination: str = Field(
        ...,
        description="The destination where the user wants to visit.",
    )


class ExtractedInfo(BaseModel):
    reasoning: str = Field(
        ...,
        description="Your reasoning under 10 words behind the extracted information.",
    )
    tour_info: Optional[TourInfo] = Field(
        None, description="The extracted tour information."
    )


TOUR_PLANNER_PROMPT = """
You're a seasoned travel planner with over 15 years of experience in creating memorable journeys. You specialize in understanding traveler needs, 
optimizing itineraries for different passenger types, and ensuring seamless travel experiences. You're particularly skilled at recognizing when 
special considerations are needed for families, seniors, and accessibility requirements.

From the user's request, you need to extract the following comprehensive information:

## Core Travel Details:
1. **Primary departure airport (IATA code)** - Select the most suitable airport considering traveler needs
2. **Alternative departure airports** - List up to 2 nearby alternatives within 200km, prioritizing family/accessibility-friendly airports
3. **Primary arrival airport (IATA code)** - Choose the most appropriate destination airport
4. **Alternative arrival airports** - List up to 2 nearby alternatives, considering ease of access and services
5. **Departure date** - Exact travel start date
6. **Return date** - Exact travel end date
7. **Destination city/location** - Main destination for planning activities

## Smart Airport Selection Guidelines:
- **For families with children**: Prioritize airports with family amenities, shorter security lines, and easier navigation
- **For senior travelers**: Choose airports with accessible services, shorter walking distances, and senior-friendly facilities
- **For mixed groups**: Balance convenience for all passenger types
- **CRITICAL**: Always provide EXACT 3-letter IATA codes (e.g., JFK, LHR, DXB) - NO CITIES OR FULL NAMES
- **Examples of smart selections**:
  * London: LHR (comprehensive services) > LGW (family-friendly) > STN (budget-focused)
  * New York: JFK (international hub) > EWR (accessible) > LGA (domestic convenience)
  * Dubai: DXB (full-service) > DWC (newer, less crowded) > SHJ (budget option)
  * Mumbai: BOM (main hub) > CCU (alternative) > DEL (connecting option)
  * Delhi: DEL (primary hub) > BOM (secondary) > CCU (tertiary)

## Traveler Intelligence:
- Analyze the request for implicit traveler information (family trip, business travel, romantic getaway, adventure travel)
- Consider seasonal factors and local events that might affect the trip
- Factor in time zones and jet lag considerations for flight timing
- Assess if special accommodations might be needed (accessibility, dietary, cultural)

## Date Intelligence:
- If no dates provided, suggest optimal travel dates considering:
  * Destination weather patterns
  * Local events and festivals
  * School holiday periods (if families involved)
  * Senior-friendly travel seasons
- Default to a 7-day trip starting from today ({date_today}) if completely unspecified
- Consider day-of-week factors for better flight prices and hotel availability

## Additional Context Analysis:
Look for hints about:
- Trip purpose (leisure, business, celebration, honeymoon, family reunion)
- Budget level (luxury, mid-range, budget)
- Activity preferences (cultural, adventure, relaxation, culinary)
- Mobility considerations (seniors, disabilities, young children)
- Special occasions (birthdays, anniversaries, graduations)

Current date: {date_today}
User's request: {query}

Extract all relevant information with intelligent assumptions based on traveler profile and trip context. Prioritize airports and timing that best serve the likely needs of the travelers."""


def extract_tour_information(query: str) -> ExtractedInfo:
    """Extract tour information using Google Gemini"""
    print("🤖 [GEMINI-DELEGATOR] Starting tour information extraction with Gemini...")
    print(f"📝 [GEMINI-DELEGATOR] Query: {query}")

    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("No API key found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")

        print("🔑 [GEMINI-DELEGATOR] API key configured for Gemini")
        genai.configure(api_key=api_key)

        # Create Gemini model
        model_name = "gemini-2.5-flash-lite"
        model = genai.GenerativeModel(model_name)
        print(f"🎯 [GEMINI-DELEGATOR] Using Gemini model: {model_name}")

        # Format the prompt with the current date
        formatted_prompt = TOUR_PLANNER_PROMPT.format(
            date_today=datetime.now().strftime("%B %d, %Y"),
            query=query
        )

        print("📤 [GEMINI-DELEGATOR] Sending request to Gemini...")
        # Use Gemini to extract information
        response = model.generate_content(formatted_prompt)

        print("✅ [GEMINI-DELEGATOR] Gemini response received")
        print(f"📄 [GEMINI-DELEGATOR] Response length: {len(response.text)} characters")
        print(f"💬 [GEMINI-DELEGATOR] Response preview: {response.text[:200]}...")

        # Parse the Gemini response to extract actual information
        # Use Gemini to intelligently extract destination from the query
        extraction_prompt = f"""
        Extract the destination city from this travel query: "{query}"

        Return only the city name, nothing else. If multiple cities are mentioned, return the destination city (not the departure city).

        Examples:
        Query: "Plan a trip from Dubai to Paris"
        Answer: Paris

        Query: "I want to visit London from New York"
        Answer: London

        Query: "Travel from Tokyo to Sydney"
        Answer: Sydney

        Query: "{query}"
        Answer:
        """

        try:
            extraction_response = model.generate_content(extraction_prompt)
            destination = extraction_response.text.strip()
            print(f"🎯 [GEMINI-DELEGATOR] Extracted destination: {destination}")
        except Exception as e:
            print(f"⚠️  [GEMINI-DELEGATOR] Failed to extract destination with Gemini: {e}")
            # Fallback: extract from query manually
            destination = extract_destination_from_query(query)
            print(f"🔄 [GEMINI-DELEGATOR] Fallback destination extraction: {destination}")

        # Extract dates from the original query
        departure_date = None
        return_date = None

        # Look for date patterns in the original query
        import re

        # Pattern 1: ISO range "from YYYY-MM-DD to YYYY-MM-DD"
        iso_pattern = r'from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})'
        iso_match = re.search(iso_pattern, query, re.IGNORECASE)
        if iso_match:
            departure_date, return_date = iso_match.groups()
        else:
            # Pattern 2: "November 1, 2025 - November 10, 2025"
            date_pattern = r'(\w+)\s+(\d+),\s*(\d{4})\s*-\s*(\w+)\s+(\d+),\s*(\d{4})'
            match = re.search(date_pattern, query)
            if match:
                start_month, start_day, start_year = match.groups()[:3]
                end_month, end_day, end_year = match.groups()[3:6]

                # Convert month names to numbers
                month_map = {
                    'january': '01', 'february': '02', 'march': '03', 'april': '04',
                    'may': '05', 'june': '06', 'july': '07', 'august': '08',
                    'september': '09', 'october': '10', 'november': '11', 'december': '12'
                }

                start_month_num = month_map.get(start_month.lower(), '01')
                end_month_num = month_map.get(end_month.lower(), '01')

                departure_date = f"{start_year}-{start_month_num}-{start_day.zfill(2)}"
                return_date = f"{end_year}-{end_month_num}-{end_day.zfill(2)}"

        # If no dates found, use default future dates
        if not departure_date:
            today = datetime.now()
            departure_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
            return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")

        print(f"📅 [GEMINI-DELEGATOR] Parsed dates - Departure: {departure_date}, Return: {return_date}")
        print(f"🎯 [GEMINI-DELEGATOR] Final destination: {destination}")

        # Ask Gemini to provide airport IATA codes dynamically (no hardcoded defaults)
        airports_prompt = f"""
Return STRICT JSON with these keys:
airport_from, alternative_airports_from (array up to 2), airport_to, alternative_airports_to (array up to 2).
Rules:
- Use valid 3-letter IATA codes.
- Choose the most appropriate primary airports for the cities.
- Provide up to 2 nearby alternatives within ~200km.
- Output ONLY JSON, no extra text.

User request: "{query}"
Destination: "{destination}"
"""

        airports_resp = model.generate_content(airports_prompt)
        airports_text = (airports_resp.text or "").strip()
        try:
            airports_data = json.loads(airports_text)
        except Exception:
            m2 = re.search(r"\{[\s\S]*\}", airports_text)
            if not m2:
                airports_data = {}
            else:
                airports_data = json.loads(m2.group(0))

        # Normalize IATA outputs
        def code_ok(code: str) -> bool:
            return bool(code) and bool(re.fullmatch(r"[A-Z]{3}", code.strip().upper()))

        airport_from = (airports_data.get("airport_from") or "").upper()
        airport_to = (airports_data.get("airport_to") or "").upper()
        alt_from = [c.strip().upper() for c in (airports_data.get("alternative_airports_from") or []) if isinstance(c, str)]
        alt_to = [c.strip().upper() for c in (airports_data.get("alternative_airports_to") or []) if isinstance(c, str)]

        if not code_ok(airport_from):
            airport_from = ""
        if not code_ok(airport_to):
            airport_to = ""
        alt_from = [c for c in alt_from if code_ok(c) and c != airport_from][:2]
        alt_to = [c for c in alt_to if code_ok(c) and c != airport_to][:2]

        # Optional fallback: use grounded structured extraction if key fields are missing
        if (not airport_from or not airport_to) and destination:
            try:
                extractor = GroundedTourExtractor()
                # extractor.extract is now synchronous; don't create nested event loops
                grounded = extractor.extract(query)
                structured = grounded.get("structured", "")
                if structured:
                    try:
                        data2 = json.loads(structured)
                        af = (data2.get("airport_from") or "").upper()
                        at = (data2.get("airport_to") or "").upper()
                        aaf = [c.strip().upper() for c in (data2.get("alternative_airports_from") or []) if isinstance(c, str)]
                        aat = [c.strip().upper() for c in (data2.get("alternative_airports_to") or []) if isinstance(c, str)]
                        if code_ok(af):
                            airport_from = af
                        if code_ok(at):
                            airport_to = at
                        if aaf:
                            alt_from = [c for c in aaf if code_ok(c) and c != airport_from][:2]
                        if aat:
                            alt_to = [c for c in aat if code_ok(c) and c != airport_to][:2]
                        dd2 = data2.get("departure_date") or departure_date
                        rd2 = data2.get("return_date") or return_date
                        if dd2:
                            departure_date = dd2
                        if rd2:
                            return_date = rd2
                    except Exception:
                        pass
            except Exception:
                pass

        return ExtractedInfo(
            reasoning="Successfully extracted tour information with Gemini",
            tour_info=TourInfo(
                airport_from=airport_from,
                alternative_airports_from=alt_from,
                airport_to=airport_to,
                alternative_airports_to=alt_to,
                departure_date=departure_date,
                return_date=return_date,
                destination=destination
            )
        )

    except Exception as e:
        print(f"❌ [GEMINI-DELEGATOR] Error: {str(e)}")
        return ExtractedInfo(
            reasoning="Failed to extract tour information with Gemini",
            tour_info=None
        )


def extract_destination_from_query(query: str) -> str:
    """
    Fallback function to extract destination from query using regex patterns
    """
    import re

    # Common patterns for destination extraction
    patterns = [
        r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "to Paris"
        r'\bvisit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "visit London"
        r'\btrip\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "trip to Tokyo"
        r'\bfrom\s+[A-Z][a-z]+\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "from Dubai to Paris"
    ]

    query_lower = query.lower()

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            destination = match.group(1).strip()
            return destination.title()  # Capitalize first letter of each word

    # If no pattern matches, try to find any city-like word
    # This is a very basic fallback
    words = query.split()
    for word in words:
        if len(word) > 3 and word[0].isupper():
            return word

    return "Unknown Destination"
