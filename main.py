from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
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
    print("🚀 [LIFESPAN] Initializing application...")
    print("✅ [LIFESPAN] Application initialized")
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
    itinerary_first: bool = Field(
        default=False,
        description="Whether to prioritize itinerary planning over flight selection"
    )
    consider_toddler_friendly: bool = Field(
        default=False,
        description="Consider toddler-friendly activities and accommodations"
    )
    consider_senior_friendly: bool = Field(
        default=False,
        description="Consider senior citizen-friendly activities and accommodations"
    )
    safety_check: bool = Field(
        default=True,
        description="Perform safety check for travel destination"
    )

    def get_dates(self) -> tuple[str, str]:
        """Returns normalized start and end dates"""
        today = datetime.now().date()
        
        # If no start_date provided, use today
        if not self.start_date:
            start = today
        else:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        
        # If no end_date provided, use start + 7 days
        if not self.end_date:
            end = start + timedelta(days=7)
        else:
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    def build_query(self) -> str:
        """Builds a structured query from the input fields"""
        query_parts = [f"Plan a trip from {self.from_city} to {self.to_city}"]
        
        if self.start_date and self.end_date:
            query_parts.append(f"from {self.start_date} to {self.end_date}")

        # Add traveler information
        traveler_info = []
        if self.travelers.adults > 0:
            traveler_info.append(f"{self.travelers.adults} adult{'s' if self.travelers.adults > 1 else ''}")
        if self.travelers.children > 0:
            traveler_info.append(f"{self.travelers.children} child{'ren' if self.travelers.children > 1 else ''}")
        if self.travelers.seniors > 0:
            traveler_info.append(f"{self.travelers.seniors} senior citizen{'s' if self.travelers.seniors > 1 else ''}")
        if self.travelers.children_under_5 > 0:
            traveler_info.append(f"{self.travelers.children_under_5} child{'ren' if self.travelers.children_under_5 > 1 else ''} under 5 years old")
        
        if traveler_info:
            query_parts.append(f"for {', '.join(traveler_info)}")

        if self.budget_amount:
            # Include concise budget context for downstream agents
            query_parts.append(f"with an overall budget of {self.budget_amount} {self.currency or 'USD'}")

        # Add special considerations
        special_considerations = []
        if self.consider_toddler_friendly:
            special_considerations.append("toddler-friendly activities and accommodations")
        if self.consider_senior_friendly:
            special_considerations.append("senior citizen-friendly activities and accommodations")
        if self.itinerary_first:
            special_considerations.append("itinerary-first planning approach")
        
        if special_considerations:
            query_parts.append(f"considering {', '.join(special_considerations)}")

        # Add flight preferences
        flight_prefs = []
        if self.flight_preferences.avoid_red_eye:
            flight_prefs.append("avoid red-eye flights")
        if self.flight_preferences.avoid_early_morning:
            flight_prefs.append("avoid early morning flights (before 8 AM)")
        if self.flight_preferences.child_friendly:
            flight_prefs.append("child-friendly flight times")
        if self.flight_preferences.senior_friendly:
            flight_prefs.append("senior-friendly flight times")
        if self.flight_preferences.direct_flights_only:
            flight_prefs.append("direct flights only")
        
        if flight_prefs:
            query_parts.append(f"with flight preferences: {', '.join(flight_prefs)}")

        if self.additional_instructions:
            query_parts.append(self.additional_instructions)
            
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

        # Build the structured query
        query = request.build_query()
        print(f"🔍 [PLAN-TRIP] Generated query: {query}")

        # Validate and normalize language (whitelist of supported codes)
        supported_langs = ["en", "hi", "es", "fr", "de", "it", "pt", "ja", "ko", "zh", "ar"]
        language = (request.language or "en").lower().strip()
        if language not in supported_langs:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}. Supported languages: {', '.join(supported_langs)}")

        print(f"🌐 [PLAN-TRIP] Language: {language}")

        # Validate required fields
        if not request.from_city or not request.to_city:
            raise HTTPException(status_code=400, detail="Both from_city and to_city are required")
        
        if request.from_city.strip().lower() == request.to_city.strip().lower():
            raise HTTPException(status_code=400, detail="Departure and destination cities cannot be the same")

        # Create workflow (Gemini used directly inside)
        workflow = TourPlannerWorkflow(language=language)

        print(f"⚙️  [PLAN-TRIP] Created workflow: {type(workflow)}")
        
        # Add timeout to prevent infinite running
        import asyncio
        try:
            print("🚀 [PLAN-TRIP] Starting workflow execution...")
            result = await asyncio.wait_for(
                workflow.run(
                    query=query,
                    budget_amount=request.budget_amount,
                    currency=(request.currency or "USD"),
                    travelers=request.travelers,
                    flight_preferences=request.flight_preferences,
                    itinerary_first=request.itinerary_first,
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
                message="Trip planning timed out. Please try again with a simpler request.",
                itinerary={
                    "flights": {"data": getattr(workflow, 'flights_data', None), "formatted": True},
                    "hotels": {"data": getattr(workflow, 'hotels_data', None), "formatted": True},
                    "places": {"data": getattr(workflow, 'places_data', None), "formatted": True},
                    "itinerary": {"data": getattr(workflow, 'itinerary', None), "formatted": True}
                }
            )
        except Exception as workflow_err:
            print(f"❌ [PLAN-TRIP] Workflow error: {workflow_err}")
            import traceback
            print(f"❌ [PLAN-TRIP] Full traceback: {traceback.format_exc()}")
            return TripResponse(
                status="error",
                message=f"Trip planning failed: {str(workflow_err)}",
                itinerary={
                    "flights": {"data": getattr(workflow, 'flights_data', None), "formatted": True},
                    "hotels": {"data": getattr(workflow, 'hotels_data', None), "formatted": True},
                    "places": {"data": getattr(workflow, 'places_data', None), "formatted": True},
                    "itinerary": {"data": getattr(workflow, 'itinerary', None), "formatted": True}
                }
            )
        print(f"🤖 [MAIN] Workflow result type: {type(result)}")
        print(f"📝 [MAIN] Result preview: {result[:200] if isinstance(result, str) else str(result)[:200]}...")

        # Structure the workflow data safely
        flights_data = getattr(workflow, 'flights_data', None)
        hotels_data = getattr(workflow, 'hotels_data', None)
        places_data = getattr(workflow, 'places_data', None)
        itinerary_data = getattr(workflow, 'itinerary', None)
        
        print(f"🔍 [MAIN] Flights data: {flights_data[:200] if flights_data else 'None'}...")
        print(f"🔍 [MAIN] Hotels data: {hotels_data[:200] if hotels_data else 'None'}...")
        print(f"🔍 [MAIN] Places data: {places_data[:200] if places_data else 'None'}...")
        print(f"🔍 [MAIN] Itinerary data: {itinerary_data[:200] if itinerary_data else 'None'}...")
        
        workflow_data = {
            "flights": {
                "data": flights_data,
                "formatted": True
            },
            "hotels": {
                "data": hotels_data,
                "formatted": True
            },
            "places": {
                "data": places_data,
                "formatted": True
            },
            "itinerary": {
                "data": itinerary_data,
                "formatted": True
            }
        }

        # Check if result is an error message
        if isinstance(result, str) and (result.startswith("Error") or result.startswith("Failed")):
            print(f"❌ [MAIN] Error in workflow: {result}")
            return TripResponse(
                status="error",
                message=result,
                itinerary=workflow_data
            )

        # Normalize workflow output to base64 PDF or markdown string
        print("✅ [MAIN] Workflow completed successfully")
        document_data: Optional[str] = None
        document_type: str = "markdown"

        try:
            # Case 1: result is a path to a generated PDF file
            if isinstance(result, str) and result.lower().endswith('.pdf') and os.path.exists(result):
                print(f"📄 [MAIN] Detected PDF file output at: {result}")
                try:
                    with open(result, 'rb') as f:
                        pdf_content = f.read()
                    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                    document_data = pdf_base64
                    document_type = "pdf"
                except Exception as file_err:
                    print(f"⚠️ [MAIN] Error reading PDF file: {file_err}")
                    document_data = str(result)
                    document_type = "markdown"

                # Clean up temp files
                try:
                    os.unlink(result)
                except Exception as cleanup_err:
                    print(f"⚠️ [MAIN] Error cleaning up PDF file: {cleanup_err}")
                
                md_file = result.replace('.pdf', '.md')
                if os.path.exists(md_file):
                    try:
                        os.unlink(md_file)
                    except Exception as md_cleanup_err:
                        print(f"⚠️ [MAIN] Error cleaning up markdown file: {md_cleanup_err}")

            # Case 2: result is a path to a markdown file
            elif isinstance(result, str) and os.path.exists(result) and result.lower().endswith('.md'):
                print(f"📝 [MAIN] Detected markdown file output at: {result}")
                try:
                    with open(result, 'r', encoding='utf-8') as f:
                        document_data = f.read()
                    document_type = "markdown"
                except Exception as file_err:
                    print(f"⚠️ [MAIN] Error reading markdown file: {file_err}")
                    document_data = str(result)
                    document_type = "markdown"
                
                try:
                    os.unlink(result)
                except Exception as cleanup_err:
                    print(f"⚠️ [MAIN] Error cleaning up markdown file: {cleanup_err}")

            # Case 3: result is raw bytes (PDF)
            elif isinstance(result, (bytes, bytearray)):
                print("📦 [MAIN] Detected binary output; encoding as base64 PDF")
                try:
                    pdf_base64 = base64.b64encode(result).decode('utf-8')
                    document_data = pdf_base64
                    document_type = "pdf"
                except Exception as encode_err:
                    print(f"⚠️ [MAIN] Error encoding binary data: {encode_err}")
                    document_data = str(result)
                    document_type = "markdown"

            # Default: treat as markdown/plain text string
            else:
                print("📝 [MAIN] Treating workflow output as markdown/text content")
                document_data = str(result)
                document_type = "markdown"
        except Exception as encode_err:
            print(f"❌ [MAIN] Error normalizing document output: {encode_err}")
            document_data = str(result) if result is not None else "No content generated"
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
        
        # Simple hardcoded authentication (you can replace with proper auth later)
        if not username:
            raise HTTPException(status_code=400, detail="Username required")
        if not password:
            raise HTTPException(status_code=400, detail="Password required")
        
        # Compare against environment-configured credentials
        valid_user = (username.lower() == (AUTH_USERNAME or "").lower())
        valid_pass = (password == (AUTH_PASSWORD or ""))
        if valid_user and valid_pass:
            return {"status": "success", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/log-download")
async def log_download():
    """Log PDF download events from client"""
    print("📥 [SERVER-LOG] PDF download initiated from client")
    print("🎯 [SERVER-LOG] Client requested PDF download")
    return {"status": "logged", "message": "Download logged"}

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
