from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, model_validator
from dotenv import load_dotenv
from workflow import TourPlannerWorkflow
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import base64
from grounding_service import GroundedFlightsSummarizer

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [LIFESPAN] Initializing Journezy Trip Planner...")
    print("✅ [LIFESPAN] Application ready")
    yield

app = FastAPI(
    title="Journezy Trip Planner",
    description="Journezy AI-powered personalized trip planner",
    version="1.0.0",
    lifespan=lifespan
)

# Load environment variables on startup
load_dotenv()

# Add template support
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Auth configuration from environment (with secure defaults and null-safety)
_env_user = os.getenv("AUTH_USERNAME")
_env_pass = os.getenv("AUTH_PASSWORD")
AUTH_USERNAME = (_env_user if _env_user is not None else "journezy").strip()
AUTH_PASSWORD = (_env_pass if _env_pass is not None else "Journezy2025!").strip()

class TravelerInfo(BaseModel):
    adults: int = Field(default=1, ge=1, le=10, description="Number of adults (1-10)")
    children: int = Field(default=0, ge=0, le=10, description="Number of children (0-10)")
    seniors: int = Field(default=0, ge=0, le=10, description="Number of senior citizens (0-10)")
    children_under_5: int = Field(default=0, ge=0, le=10, description="Number of children under 5 years old")
    itinerary_based_passengers: bool = Field(default=False, description="Whether to consider passenger types in itinerary planning")

class FlightPreferences(BaseModel):
    avoid_red_eye: bool = Field(default=False, description="Avoid red-eye flights")
    avoid_early_morning: bool = Field(default=False, description="Avoid early morning flights (before 8 AM)")
    child_friendly: bool = Field(default=False, description="Prefer child-friendly flight times")
    senior_friendly: bool = Field(default=False, description="Prefer senior-friendly flight times")
    direct_flights_only: bool = Field(default=False, description="Prefer direct flights only")

class TripRequest(BaseModel):
    from_city: str = Field(..., description="Departure city")
    to_city: str = Field(..., description="Destination city")
    additional_instructions: Optional[str] = Field(
        default="",
        description="Additional instructions or preferences for the trip"
    )
    language: str = Field(
        default="en",
        description="Language code for the itinerary (e.g., en, hi, es, fr, de, it, pt, ja, ko, zh, ar)"
    )
    start_date: Optional[str] = Field(
        default=None, 
        description="Start date in YYYY-MM-DD format. If not provided, defaults to today"
    )
    end_date: Optional[str] = Field(
        default=None, 
        description="End date in YYYY-MM-DD format. If not provided, defaults to start_date + 7 days"
    )
    budget_amount: Optional[float] = Field(
        default=None,
        description="Overall trip budget in selected currency (optional)"
    )
    currency: Optional[str] = Field(
        default="USD",
        description="Currency code for the budget and display (USD or INR)"
    )
    travelers: TravelerInfo = Field(
        default_factory=TravelerInfo,
        description="Traveler information including adults, children, seniors"
    )
    flight_preferences: FlightPreferences = Field(
        default_factory=FlightPreferences,
        description="Flight preferences and constraints"
    )
    consider_toddler_friendly: bool = Field(
        default=False,
        description="Consider toddler-friendly activities and accommodations"
    )
    consider_senior_friendly: bool = Field(
        default=False,
        description="Consider senior citizen-friendly activities and accommodations"
    )
    wheelchair_accessible: bool = Field(
        default=False,
        description="Prioritize wheelchair-accessible venues and transportation"
    )
    vegetarian_preference: bool = Field(
        default=False,
        description="Include vegetarian dining options and restaurants"
    )
    non_vegetarian_preference: bool = Field(
        default=False,
        description="Include local meat and seafood specialties"
    )
    safety_check: bool = Field(
        default=True,
        description="Perform safety check for travel destination"
    )

    @model_validator(mode='before')
    @classmethod
    def validate_required_objects(cls, values):
        """Ensure required objects are never None"""
        if isinstance(values, dict):
            if values.get('flight_preferences') is None:
                values['flight_preferences'] = {}
            if values.get('travelers') is None:
                values['travelers'] = {}
        return values

    def get_dates(self) -> tuple[str, str]:
        """Returns normalized start and end dates with validation"""
        today = datetime.now().date()
        
        # If no start_date provided, use today
        if not self.start_date:
            start = today
        else:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            # Validate start date is not in the past
            if start < today:
                start = today  # Auto-correct to today if in the past
        
        # If no end_date provided, use start + 7 days
        if not self.end_date:
            end = start + timedelta(days=7)
        else:
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            # Validate end date is not before start date
            if end < start:
                end = start + timedelta(days=7)  # Auto-correct to start + 7 days
            
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    def build_query(self) -> str:
        """Builds a comprehensive, structured query from the input fields with detailed context"""
        
        # Use get_dates() to ensure we have proper date strings
        start_date, end_date = self.get_dates()
        
        # Calculate trip duration for intelligent planning
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            duration_days = (end_dt - start_dt).days
        except Exception:
            duration_days = 7  # Default fallback
        
        # Build comprehensive trip description
        query_parts = []
        
        # 1. Basic trip structure with intelligent context
        query_parts.append(f"Plan a comprehensive {duration_days}-day trip from {self.from_city} to {self.to_city}")
        query_parts.append(f"from {start_date} to {end_date}")

        # 2. Detailed traveler profile analysis
        traveler_profile = []
        total_travelers = 0
        
        if self.travelers.adults > 0:
            traveler_profile.append(f"{self.travelers.adults} adult{'s' if self.travelers.adults > 1 else ''}")
            total_travelers += self.travelers.adults
            
        if self.travelers.children > 0:
            traveler_profile.append(f"{self.travelers.children} child{'ren' if self.travelers.children > 1 else ''}")
            total_travelers += self.travelers.children
            
        if self.travelers.seniors > 0:
            traveler_profile.append(f"{self.travelers.seniors} senior citizen{'s' if self.travelers.seniors > 1 else ''}")
            total_travelers += self.travelers.seniors
            
        if self.travelers.children_under_5 > 0:
            traveler_profile.append(f"{self.travelers.children_under_5} toddler{'s' if self.travelers.children_under_5 > 1 else ''} (under 5 years)")
            total_travelers += self.travelers.children_under_5
        
        if traveler_profile:
            query_parts.append(f"for a group of {total_travelers}: {', '.join(traveler_profile)}")

        # 3. Trip characteristics and group dynamics
        trip_characteristics = []
        
        # Determine trip type based on traveler composition
        if self.travelers.children > 0 or self.travelers.children_under_5 > 0:
            if self.travelers.seniors > 0:
                trip_characteristics.append("multi-generational family trip")
            else:
                trip_characteristics.append("family trip with children")
        elif self.travelers.seniors > 0:
            trip_characteristics.append("senior-friendly travel experience")
        elif self.travelers.adults == 2 and total_travelers == 2:
            trip_characteristics.append("couples getaway")
        elif self.travelers.adults > 2:
            trip_characteristics.append("group travel experience")
        
        # Add duration context
        if duration_days <= 3:
            trip_characteristics.append("short city break")
        elif duration_days <= 7:
            trip_characteristics.append("week-long vacation")
        elif duration_days <= 14:
            trip_characteristics.append("extended holiday")
        else:
            trip_characteristics.append("long-term travel experience")
        
        if trip_characteristics:
            query_parts.append(f"This is a {', '.join(trip_characteristics)}.")

        # 4. Budget context with intelligence
        if self.budget_amount and self.budget_amount > 0:
            currency_symbol = "$" if (self.currency or "USD").upper() == "USD" else "₹"
            per_person_budget = self.budget_amount / max(total_travelers, 1)
            
            # Determine budget category
            budget_category = ""
            if per_person_budget < 100:
                budget_category = "budget-conscious"
            elif per_person_budget < 500:
                budget_category = "mid-range"
            elif per_person_budget < 1500:
                budget_category = "comfortable"
            else:
                budget_category = "luxury"
            
            query_parts.append(f"Total budget: {currency_symbol}{self.budget_amount:,.0f} {self.currency or 'USD'} ({budget_category} travel style, approximately {currency_symbol}{per_person_budget:,.0f} per person)")

        # 5. Accessibility and special requirements
        accessibility_needs = []
        if self.consider_toddler_friendly:
            accessibility_needs.extend([
                "toddler-friendly accommodations with cribs and high chairs",
                "stroller-accessible attractions and venues",
                "child-safe environments and activities",
                "family-friendly dining options with kids menus"
            ])
            
        if self.consider_senior_friendly:
            accessibility_needs.extend([
                "senior-friendly accommodations with elevator access",
                "accessible attractions and venues",
                "comfortable seating and rest areas",
                "easy-to-navigate locations with minimal walking"
            ])
        
        if self.wheelchair_accessible:
            accessibility_needs.extend([
                "wheelchair-accessible accommodations with ramps and elevators",
                "barrier-free attractions and venues",
                "accessible transportation options",
                "wide doorways and accessible bathrooms"
            ])
        
        # 5b. Food preferences
        food_preferences = []
        if self.vegetarian_preference:
            food_preferences.append("include vegetarian and vegan dining options")
        if self.non_vegetarian_preference:
            food_preferences.append("include local meat and seafood specialties")
        
        if accessibility_needs:
            query_parts.append(f"Special requirements include: {', '.join(accessibility_needs)}")
        
        if food_preferences:
            query_parts.append(f"Dining preferences: {', '.join(food_preferences)}")

        # 6. Comprehensive flight preferences with reasoning
        flight_requirements = []
        if self.flight_preferences:
            if self.flight_preferences.avoid_red_eye:
                flight_requirements.append("avoid red-eye flights (departures between 10 PM - 6 AM) for better rest")
            if self.flight_preferences.avoid_early_morning:
                flight_requirements.append("avoid early morning departures (before 8 AM) for comfortable travel")
            if self.flight_preferences.child_friendly:
                flight_requirements.append("prioritize child-friendly flight times (mid-day departures 10 AM - 6 PM) with family seating")
            if self.flight_preferences.senior_friendly:
                flight_requirements.append("prefer senior-friendly flight times (10 AM - 4 PM) with assistance services available")
            if self.flight_preferences.direct_flights_only:
                flight_requirements.append("direct flights only to minimize travel fatigue and connection stress")
        
        if flight_requirements:
            query_parts.append(f"Flight preferences: {', '.join(flight_requirements)}")

        # 7. Safety and health considerations
        safety_notes = []
        if self.safety_check:
            safety_notes.append("include current travel safety information and health advisories")
            
        if self.travelers.seniors > 0:
            safety_notes.append("provide senior health and mobility considerations")
            
        if self.travelers.children > 0 or self.travelers.children_under_5 > 0:
            safety_notes.append("include child safety guidelines and family emergency procedures")
        
        if safety_notes:
            query_parts.append(f"Safety requirements: {', '.join(safety_notes)}")

        # 8. Additional context and preferences
        if self.additional_instructions:
            query_parts.append(f"Additional preferences: {self.additional_instructions}")

        # 9. Planning intelligence requirements
        intelligence_requirements = [
            "create a balanced itinerary with cultural experiences, local cuisine, and authentic attractions",
            "optimize logistics to minimize travel time between activities",
            "include weather considerations and seasonal recommendations",
            "provide local transportation guidance and accessibility information",
            "suggest authentic dining experiences suitable for the traveler profile"
        ]
        
        if duration_days >= 5:
            intelligence_requirements.append("include at least one rest/flexibility day for spontaneous activities")
            
        query_parts.append(f"Planning requirements: {'; '.join(intelligence_requirements)}")

        return " ".join(query_parts)

class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Dict[str, Any]  # Raw workflow data
    document: Optional[str] = None  # PDF/Markdown content
    document_type: Optional[str] = None  # "pdf" or "markdown"

class BrowserSearchRequest(BaseModel):
    search_type: str = Field(..., description="Type of search: 'flights', 'hotels', or 'places'")
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    city: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    date: Optional[str] = None

class BrowserSearchResponse(BaseModel):
    status: str
    message: str
    data: str

class GroundedFlightsRequest(BaseModel):
    query: str
    flights_text: str

class GroundedFlightsResponse(BaseModel):
    status: str
    message: str
    summary: str
    citations: list[str]

class SafetyCheckRequest(BaseModel):
    destination: str = Field(..., description="Destination city/country to check safety for")
    travelers: TravelerInfo = Field(default_factory=TravelerInfo, description="Traveler information for safety considerations")

class SafetyCheckResponse(BaseModel):
    status: str
    message: str
    safety_info: Dict[str, Any]
    travel_advisories: list[str]
    recommendations: list[str]

@app.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    try:
        print("🎯 [PLAN-TRIP] Starting trip planning request...")
        print(f"📝 [PLAN-TRIP] Request: {request.from_city} -> {request.to_city}")

        start_date, end_date = request.get_dates()
        print(f"📅 [PLAN-TRIP] Trip dates: {start_date} to {end_date}")

        # Build the structured query
        query = request.build_query()
        print(f"🔍 [PLAN-TRIP] Generated query: {query}")
        
        # Ensure dates are properly formatted strings
        if not isinstance(start_date, str):
            start_date = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)
        if not isinstance(end_date, str):
            end_date = end_date.strftime("%Y-%m-%d") if hasattr(end_date, 'strftime') else str(end_date)

        # Validate and normalize language (whitelist of supported codes)
        supported_langs = ["en", "hi", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar"]
        language = (request.language or "en").lower().strip()
        if language not in supported_langs:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}. Supported languages: {', '.join(supported_langs)}")

        print(f"🌐 [PLAN-TRIP] Language: {language}")

        # Validate required fields
        if not request.from_city or not request.to_city:
            raise HTTPException(status_code=400, detail="Both from_city and to_city are required")
        
        # Validate city names are not empty after stripping
        if not request.from_city.strip() or not request.to_city.strip():
            raise HTTPException(status_code=400, detail="City names cannot be empty")
        
        if request.from_city.strip().lower() == request.to_city.strip().lower():
            raise HTTPException(status_code=400, detail="Departure and destination cities cannot be the same")

        # Create workflow (Gemini used directly inside)
        workflow = TourPlannerWorkflow(language=language)

        print(f"⚙️  [PLAN-TRIP] Created workflow: {type(workflow)}")
        
        # Add timeout to prevent infinite running
        import asyncio
        try:
            print("🚀 [PLAN-TRIP] Starting workflow execution...")
            print(f"📊 [PLAN-TRIP] Smart defaults: toddler_friendly={request.consider_toddler_friendly}, senior_friendly={request.consider_senior_friendly}")
            print(f"🧳 [PLAN-TRIP] Travelers: {request.travelers.adults} adults, {request.travelers.children} children, {request.travelers.seniors} seniors")
            print(f"✈️  [PLAN-TRIP] Flight prefs: child_friendly={request.flight_preferences.child_friendly}, senior_friendly={request.flight_preferences.senior_friendly}")
            
            result = await asyncio.wait_for(
                workflow.run(
                    query=query,
                    budget_amount=request.budget_amount,
                    currency=(request.currency or "USD"),
                    travelers=request.travelers,
                    flight_preferences=request.flight_preferences,
                    consider_toddler_friendly=request.consider_toddler_friendly,
                    consider_senior_friendly=request.consider_senior_friendly,
                    safety_check=request.safety_check
                ),
                timeout=300.0  # 5 minutes timeout
            )
            print("✅ [PLAN-TRIP] Workflow execution completed successfully")
        except asyncio.TimeoutError:
            print("⏰ [PLAN-TRIP] Request timed out after 5 minutes")
            return TripResponse(
                status="error",
                message="Trip planning timed out after 5 minutes. This may happen with complex requests. Please try again with a simpler request or check your internet connection.",
                itinerary={
                    "flights": {"data": getattr(workflow, 'flights_data', None), "formatted": True},
                    "hotels": {"data": getattr(workflow, 'hotels_data', None), "formatted": True},
                    "places": {"data": getattr(workflow, 'places_data', None), "formatted": True},
                    "itinerary": {"data": getattr(workflow, 'itinerary', None), "formatted": True}
                },
                document=None,
                document_type="markdown"
            )
        except Exception as workflow_err:
            print(f"❌ [PLAN-TRIP] Workflow error: {workflow_err}")
            import traceback
            print("❌ [PLAN-TRIP] Full traceback: " + traceback.format_exc())
            return TripResponse(
                status="error",
                message=f"Trip planning failed: {str(workflow_err)}",
                itinerary={
                    "flights": {"data": getattr(workflow, 'flights_data', None), "formatted": True},
                    "hotels": {"data": getattr(workflow, 'hotels_data', None), "formatted": True},
                    "places": {"data": getattr(workflow, 'places_data', None), "formatted": True},
                    "itinerary": {"data": getattr(workflow, 'itinerary', None), "formatted": True}
                },
                document=None,
                document_type="markdown"
            )
        print(f"🤖 [MAIN] Workflow result type: {type(result)}")
        print(f"📝 [MAIN] Result preview: {result[:200] if isinstance(result, str) else str(result)[:200]}...")

        # Structure the workflow data
        workflow_data = {
            "flights": {
                "data": workflow.flights_data if hasattr(workflow, 'flights_data') else None,
                "formatted": True
            },
            "hotels": {
                "data": workflow.hotels_data if hasattr(workflow, 'hotels_data') else None,
                "formatted": True
            },
            "places": {
                "data": workflow.places_data if hasattr(workflow, 'places_data') else None,
                "formatted": True
            },
            "itinerary": {
                "data": workflow.itinerary if hasattr(workflow, 'itinerary') else None,
                "formatted": True
            }
        }

        # Check if result is an error message
        if isinstance(result, str) and (result.startswith("Error") or result.startswith("Failed")):
            print(f"❌ [MAIN] Error in workflow: {result}")
            return TripResponse(
                status="error",
                message=result,
                itinerary=workflow_data,
                document=None,
                document_type="markdown"
            )

        # Handle workflow output - now returns base64 PDF directly
        print("✅ [MAIN] Workflow completed successfully")
        document_data: Optional[str] = None
        document_type: str = "pdf"  # Default to PDF since workflow now generates PDFs

        try:
            if isinstance(result, str):
                # Check if it's a base64-encoded PDF (new workflow behavior)
                if len(result) > 1000 and not any(char in result for char in ['\n', '#', '*', '-']):
                    # Likely base64 PDF data
                    print("📄 [MAIN] Detected base64 PDF output from workflow")
                    document_data = result
                    document_type = "pdf"
                    
                    # Validate it's actually PDF data
                    try:
                        # Quick validation: decode a small portion to check PDF signature
                        test_decode = base64.b64decode(result[:100])
                        if test_decode.startswith(b'%PDF'):
                            print("✅ [MAIN] Validated PDF signature in base64 data")
                        else:
                            print("⚠️ [MAIN] Base64 data doesn't appear to be a valid PDF, treating as text")
                            document_data = result
                            document_type = "markdown"
                    except Exception as validation_err:
                        print(f"⚠️ [MAIN] PDF validation failed: {validation_err}, treating as text")
                        document_data = result
                        document_type = "markdown"
                
                # Check if it's a file path
                elif os.path.exists(result):
                    if result.lower().endswith('.pdf'):
                        print(f"📄 [MAIN] Detected PDF file output at: {result}")
                        try:
                            with open(result, 'rb') as f:
                                pdf_content = f.read()
                            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                            document_data = pdf_base64
                            document_type = "pdf"
                            print(f"✅ [MAIN] Successfully encoded PDF file to base64")
                        except Exception as file_err:
                            print(f"❌ [MAIN] Error reading PDF file: {file_err}")
                            document_data = result
                            document_type = "markdown"

                        # Clean up temp file
                        try:
                            os.unlink(result)
                            print(f"🧹 [MAIN] Cleaned up temp PDF file: {result}")
                        except Exception as cleanup_err:
                            print(f"⚠️ [MAIN] Error cleaning up PDF file: {cleanup_err}")
                
                # Handle .pdf in result string (reference format)
                elif ".pdf" in result:
                    with open(result, 'rb') as f:
                        pdf_content = f.read()
                    # Convert binary PDF to base64
                    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                    document_data = pdf_base64
                    document_type = "pdf"
                    
                elif result.lower().endswith('.md'):
                    print(f"📝 [MAIN] Detected markdown file output at: {result}")
                    try:
                        with open(result, 'r', encoding='utf-8') as f:
                            document_data = f.read()
                        document_type = "markdown"
                        print(f"✅ [MAIN] Successfully read markdown file")
                    except Exception as file_err:
                        print(f"❌ [MAIN] Error reading markdown file: {file_err}")
                        document_data = result
                        document_type = "markdown"
                        
                    # Clean up temp file
                    try:
                        os.unlink(result)
                        print(f"🧹 [MAIN] Cleaned up temp markdown file: {result}")
                    except Exception as cleanup_err:
                        print(f"⚠️ [MAIN] Error cleaning up markdown file: {cleanup_err}")
                else:
                    print(f"📝 [MAIN] Unknown file type, treating as text: {result}")
                    document_data = result
                    document_type = "markdown"
            
            # Handle binary data (fallback case)
            elif isinstance(result, (bytes, bytearray)):
                print("📦 [MAIN] Detected binary output; encoding as base64 PDF")
                try:
                    pdf_base64 = base64.b64encode(result).decode('utf-8')
                    document_data = pdf_base64
                    document_type = "pdf"
                    print(f"✅ [MAIN] Successfully encoded binary data to base64")
                except Exception as encode_err:
                    print(f"❌ [MAIN] Error encoding binary data: {encode_err}")
                    document_data = str(result)
                    document_type = "markdown"
            
            # Handle None or other types
            else:
                print(f"⚠️ [MAIN] Unexpected result type: {type(result)}")
                document_data = str(result) if result is not None else "No content generated"
                document_type = "markdown"
                
        except Exception as process_err:
            print(f"❌ [MAIN] Error processing workflow output: {process_err}")
            import traceback
            print(f"❌ [MAIN] Processing error traceback: {traceback.format_exc()}")
            document_data = str(result) if result is not None else "Error processing workflow output"
            document_type = "markdown"

        print(f"📄 [MAIN] Document payload length: {len(document_data) if document_data else 0} characters")
        print(f"📋 [MAIN] Document type: {document_type}")
        print("🎯 [MAIN] Sending document data to client for download")

        return TripResponse(
            status="success",
            message="Trip planned successfully with Gemini 2.5 flash-lite",
            itinerary=workflow_data,
            document=document_data,
            document_type=document_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grounded-flights", response_model=GroundedFlightsResponse)
async def grounded_flights(req: GroundedFlightsRequest):
    try:
        if not req.query or not req.flights_text:
            raise HTTPException(status_code=400, detail="Both query and flights_text are required")
        
        summarizer = GroundedFlightsSummarizer()
        result = await summarizer.summarize_flights(req.query, req.flights_text)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate grounded summary")
        
        return GroundedFlightsResponse(
            status="success",
            message="Grounded summary generated",
            summary=result.get("text", ""),
            citations=result.get("citations", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [GROUNDED-FLIGHTS] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/safety-check", response_model=SafetyCheckResponse)
async def safety_check(req: SafetyCheckRequest):
    try:
        if not req.destination or not req.destination.strip():
            raise HTTPException(status_code=400, detail="Destination is required")
        
        print(f"🔍 [SAFETY-CHECK] Checking safety for destination: {req.destination}")
        
        # Basic safety information (in a real implementation, this would call external APIs)
        safety_info = {
            "destination": req.destination.strip(),
            "overall_risk": "Low to Moderate",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "traveler_types": {
                "adults": req.travelers.adults,
                "children": req.travelers.children,
                "seniors": req.travelers.seniors,
                "children_under_5": req.travelers.children_under_5
            }
        }
        
        # Generate travel advisories based on destination and traveler types
        advisories = []
        recommendations = []
        
        # General advisories
        advisories.append("Check local COVID-19 requirements and restrictions")
        advisories.append("Verify visa requirements for your nationality")
        advisories.append("Register with your embassy if traveling internationally")
        
        # Traveler-specific recommendations
        if req.travelers.children > 0:
            recommendations.append("Ensure children have proper identification and emergency contacts")
            recommendations.append("Research child-friendly medical facilities at destination")
        
        if req.travelers.seniors > 0:
            recommendations.append("Consider travel insurance with medical coverage")
            recommendations.append("Research accessible transportation options")
        
        if req.travelers.children_under_5 > 0:
            recommendations.append("Pack essential medications and first aid supplies")
            recommendations.append("Research pediatric medical facilities")
        
        # Destination-specific recommendations (basic)
        if "europe" in req.destination.lower():
            recommendations.append("Consider travel insurance for medical emergencies")
        elif "asia" in req.destination.lower():
            recommendations.append("Check vaccination requirements")
        elif "africa" in req.destination.lower():
            recommendations.append("Consult with travel medicine specialist")
        
        return SafetyCheckResponse(
            status="success",
            message="Safety check completed",
            safety_info=safety_info,
            travel_advisories=advisories,
            recommendations=recommendations
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [SAFETY-CHECK] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def read_root():
    """Serve the login page"""
    try:
        if not os.path.exists('static/login.html'):
            raise HTTPException(status_code=404, detail="Login page not found")
        return FileResponse('static/login.html')
    except Exception as e:
        print(f"❌ [ROOT] Error serving login page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login")
async def login(request: Request):
    """Handle login authentication"""
    try:
        content_type = (request.headers.get("content-type") or "").lower()
        username = None
        password = None

        # Accept both JSON and form-urlencoded
        if "application/json" in content_type:
            try:
                data = await request.json()
                username = (data.get("username") or "").strip()
                password = (data.get("password") or "").strip()
            except Exception as json_err:
                print(f"⚠️ [LOGIN] JSON parsing error: {json_err}")
                username = None
                password = None
        
        if username is None or password is None:
            try:
                form_data = await request.form()
                username = (form_data.get("username") or "").strip()
                password = (form_data.get("password") or "").strip()
            except Exception as form_err:
                print(f"⚠️ [LOGIN] Form parsing error: {form_err}")
                raise HTTPException(status_code=400, detail="Invalid request format")
        
        # Input validation
        if not username or len(username.strip()) == 0:
            raise HTTPException(status_code=400, detail="Username required")
        if not password or len(password.strip()) == 0:
            raise HTTPException(status_code=400, detail="Password required")
        
        # Length limits for security
        if len(username) > 100:
            raise HTTPException(status_code=400, detail="Username too long")
        if len(password) > 200:
            raise HTTPException(status_code=400, detail="Password too long")
        
        print(f"🔐 [LOGIN] Authentication attempt for user: {username}")
        
        # Compare against environment-configured credentials
        valid_user = (username.lower() == (AUTH_USERNAME or "").lower())
        valid_pass = (password == (AUTH_PASSWORD or ""))
        
        if valid_user and valid_pass:
            print(f"✅ [LOGIN] Successful authentication for user: {username}")
            return {"status": "success", "message": "Login successful"}
        else:
            print(f"❌ [LOGIN] Failed authentication attempt for user: {username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log-download")
async def log_download():
    """Log PDF download events from client"""
    print("📥 [SERVER-LOG] PDF download initiated from client")
    print("🎯 [SERVER-LOG] Client requested PDF download")
    return {"status": "logged", "message": "Download logged"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend status"""
    try:
        # Check critical components
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "workflow": "ok",
                "agents": "ok",
                "tools": "ok",
                "environment": "ok"
            }
        }
        
        # Test critical imports
        try:
            import workflow
            import agents.deligator
            import tools.flights
            health_status["components"]["workflow"] = "ok"
        except Exception as e:
            health_status["components"]["workflow"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check environment variables
        required_env = ["GOOGLE_API_KEY", "AUTH_USERNAME", "AUTH_PASSWORD"]
        missing_env = [var for var in required_env if not os.getenv(var)]
        if missing_env:
            health_status["components"]["environment"] = f"missing: {', '.join(missing_env)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/app")
async def read_app():
    """Serve the main application page"""
    try:
        if not os.path.exists('templates/index.html'):
            raise HTTPException(status_code=404, detail="Application page not found")
        return FileResponse('templates/index.html')
    except Exception as e:
        print(f"❌ [APP] Error serving application page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
