from typing import Optional
import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def format_minutes(total_minutes):
    try:
        # Ensure the input is a non-negative integer
        if not isinstance(total_minutes, int) or total_minutes < 0:
            raise ValueError("Total minutes must be a non-negative integer.")
        hours = total_minutes // 60  # Calculate hours
        minutes = total_minutes % 60  # Calculate remaining minutes
        # Format the output based on hours and minutes
        if hours > 0 and minutes > 0:
            return f"{hours} hr {minutes} min"
        elif hours > 0:
            return f"{hours} hr"
        else:
            return f"{minutes} min"
    except Exception as e:
        raise ValueError(f"Failed to format minutes: {str(e)}")


def _flight_meets_preferences(flight, avoid_red_eye, avoid_early_morning, child_friendly, senior_friendly):
    """Check if a flight meets the specified preferences"""
    try:
        # Extract departure time from flight data
        departure_time = None
        for part in flight.get("flights", []):
            dep_airport = part.get("departure_airport", {})
            if dep_airport.get("time"):
                departure_time = dep_airport["time"]
                break
        
        if not departure_time:
            return True  # If no time info, include the flight
        
        # Parse time (assuming format like "14:30" or "2:30 PM")
        import re
        time_match = re.search(r'(\d{1,2}):(\d{2})', departure_time)
        if not time_match:
            return True  # If can't parse time, include the flight
        
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        
        # Check for red-eye flights (typically 10 PM to 6 AM)
        if avoid_red_eye:
            if hour >= 22 or hour < 6:
                return False
        
        # Check for early morning flights (before 8 AM)
        if avoid_early_morning:
            if hour < 8:
                return False
        
        # For child/senior friendly, prefer mid-day flights (10 AM to 6 PM)
        if child_friendly or senior_friendly:
            if hour < 10 or hour >= 18:
                return False
        
        return True
    except Exception:
        return True  # If any error, include the flight


def format_one_flight(
    flight_no: str,
    dep_port: str,
    arr_port: str,
    dep_time: str,
    arr_time: str,
    duration: int,
    airline: str,
    airplane: str,
) -> str:
    # Ensure we have readable timing format
    dep_time_clean = dep_time.replace('AM', ' AM').replace('PM', ' PM') if dep_time else 'N/A'
    arr_time_clean = arr_time.replace('AM', ' AM').replace('PM', ' PM') if arr_time else 'N/A'
    duration_clean = format_minutes(duration) if duration else 'N/A'
    
    # Debug only when there are issues with the data
    if dep_time == 'N/A' or arr_time == 'N/A' or duration == 0:
        print(f"⚠️ [FORMAT-ONE-FLIGHT] Missing data - Times: {dep_time}/{arr_time}, Duration: {duration}")
    
    result = f"{airline} {flight_no} - {dep_port} ({dep_time_clean}) -> {arr_port} ({arr_time_clean}) [{duration_clean}] - {airplane}"
    return result


def get_formatted_flights_info(flights: list, currency_code: str = "USD") -> str:
    # Ensure consistent currency symbol mapping
    currency_upper = currency_code.upper()
    if currency_upper == "USD":
        symbol = "$"
    elif currency_upper == "INR":
        symbol = "₹" 
    else:
        symbol = "$"  # Default fallback
        
    formatted_flights = []
    for flight in flights:
        for part in flight["flights"]:
            # Ensure all flight data fields exist with fallbacks
            flight_number = part.get("flight_number", "N/A")
            dep_airport_id = part.get("departure_airport", {}).get("id", "N/A")
            arr_airport_id = part.get("arrival_airport", {}).get("id", "N/A")
            dep_time = part.get("departure_airport", {}).get("time", "N/A")
            arr_time = part.get("arrival_airport", {}).get("time", "N/A")
            duration = part.get("duration", 0)
            airline = part.get("airline", "Unknown Airline")
            airplane = part.get("airplane", "N/A")
            
            # Debug only if time extraction fails
            if dep_time == "N/A" or arr_time == "N/A":
                print(f"⚠️ [FLIGHT-FORMAT] Missing time data - Departure: {dep_time}, Arrival: {arr_time}")
                print(f"⚠️ [FLIGHT-FORMAT] Full part data: {part}")
            
            formatted_flight_line = format_one_flight(
                flight_number,
                dep_airport_id,
                arr_airport_id,
                dep_time,
                arr_time,
                duration,
                airline,
                airplane,
            )
            formatted_flights.append(formatted_flight_line)
        if "layovers" in flight and len(flight["layovers"]) > 0:
            layover_duration = flight["layovers"][0].get("duration", 0)
            layover_id = flight["layovers"][0].get("id", "Unknown")
            formatted_flights.append(
                f"Layover at {layover_id}: {format_minutes(layover_duration)}"
            )
        
        total_duration = flight.get("total_duration", 0)
        formatted_flights.append(
            f"Total Duration: {format_minutes(total_duration)}"
        )
        
        # Ensure price formatting is consistent
        price = flight.get("price", 0)
        try:
            # Remove any existing currency symbols from price
            price_clean = str(price).replace("$", "").replace("₹", "").replace(",", "")
            price_float = float(price_clean)
            formatted_flights.append(f"Price ({currency_upper}): {symbol}{price_float:,.0f}")
        except (ValueError, TypeError):
            formatted_flights.append(f"Price ({currency_upper}): {symbol}N/A")
        
        formatted_flights.append("")
    
    final_output = "\n".join(formatted_flights)
    
    # Only debug if there seems to be an issue with the output
    if "N/A" in final_output:
        print(f"⚠️ [FLIGHT-FORMAT] Output contains N/A values:")
        print(f"📄 [FLIGHT-FORMAT] {final_output}")
    
    return final_output


def find_flights(
    departure_airport: str = Field(
        ..., description="The 3 letter departure airport code (IATA) e.g. LHR"
    ),
    arrival_airport: str = Field(
        ..., description="The 3 letter arrival airport code (IATA) e.g. JFK"
    ),
    departure_date: str = Field(
        ..., description="The departure date in the format YYYY-MM-DD"
    ),
    return_date: Optional[str] = Field(
        None, description="The return date in the format YYYY-MM-DD"
    ),
    currency: str = "USD",
    avoid_red_eye: bool = False,
    avoid_early_morning: bool = False,
    child_friendly: bool = False,
    senior_friendly: bool = False,
    direct_flights_only: bool = False,
) -> str:
    """
    Find flights between two airports on given dates.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    
    # Set stops based on preferences
    stops = 0 if direct_flights_only else 2  # 0 for direct only, 2 for 1 stop or less
    
    params = {
        "engine": "google_flights",
        "hl": "en",
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": departure_date,
        "return_date": return_date,
        "stops": stops,
        "currency": currency,
        "api_key": SERPAPI_KEY,
    }
    if return_date:
        params["type"] = "1"  # Round Trip (Default selection)
    else:
        params["type"] = "2"  # One Way

    # Add debug prints
    print("\n=== DEBUG: SerpAPI Request Parameters ===")
    print(f"Departure Airport: {departure_airport}")
    print(f"Arrival Airport: {arrival_airport}")
    print(f"Departure Date: {departure_date}")
    print(f"Return Date: {return_date}")
    print("Full params:")
    print(params)
    print("=======================================\n")

    try:
        print(f"\n> Finding flights from {departure_airport} to {arrival_airport}\n")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Add debug print for API response
        print("\n=== DEBUG: SerpAPI Response ===")
        print(results)
        print("==============================\n")
        
        if "error" in results:
            raise ValueError(f"SerpAPI error: {results['error']}")
        # Merge best and other flights, then filter based on preferences
        flights_data_all = (results.get("best_flights") or []) + (results.get("other_flights") or [])
        
        # Filter flights based on preferences
        filtered_flights = []
        for flight in flights_data_all:
            # Check if flight meets preference criteria
            if _flight_meets_preferences(flight, avoid_red_eye, avoid_early_morning, 
                                      child_friendly, senior_friendly):
                filtered_flights.append(flight)
        
        # If no flights meet preferences, use all flights
        if not filtered_flights:
            filtered_flights = flights_data_all
        
        # Sort by price and take top 3
        def _price_key(f):
            try:
                return float(f.get("price", 1e12))
            except Exception:
                return 1e12
        filtered_flights.sort(key=_price_key)
        flights_data = filtered_flights[:3]
        
        first_line = f"Flights from {departure_airport} to {arrival_airport}:"
        if avoid_red_eye or avoid_early_morning or child_friendly or senior_friendly or direct_flights_only:
            first_line += " (filtered by preferences)"
        return first_line + "\n\n" + get_formatted_flights_info(flights_data[:3], currency_code=currency)
    except Exception as e:
        raise Exception(f"Failed to search flights: {str(e)}")
