from typing import Any
from datetime import datetime, timedelta
import os
import tempfile
import base64
import gh_md_to_html
import pdfkit
import asyncio

from tools.flights import find_flights
from grounding_service import GroundedFlightFinder
from tools.hotels import find_hotels
from tools.places import find_places_to_visit

from agents.deligator import extract_tour_information
from agents.itinerary_writer import write_itinerary
# Currency conversion not required; fetch data in user-selected currency via SerpAPI




class TourPlannerWorkflow:
    def __init__(
        self,
        *args: Any,
        language: str = "english",
        **kwargs: Any,
    ) -> None:
        self.language = language
        self.flights_data = ""
        self.hotels_data = ""
        self.places_data = ""
        self.itinerary = ""
        self.travelers = None
        self.flight_preferences = None
        self.consider_toddler_friendly = False
        self.consider_senior_friendly = False
        self.safety_check = True

    async def run(self, query: str, *, budget_amount: float | None = None, currency: str = "USD", 
                  travelers=None, flight_preferences=None,
                  consider_toddler_friendly: bool = False, consider_senior_friendly: bool = False,
                  safety_check: bool = True) -> str:
        """Main workflow execution using Gemini directly"""
        print("🤖 [WORKFLOW] Starting workflow...")
        print(f"📝 [WORKFLOW] Query: {query}")

        # Store the new parameters
        self.travelers = travelers
        self.flight_preferences = flight_preferences
        self.consider_toddler_friendly = consider_toddler_friendly
        self.consider_senior_friendly = consider_senior_friendly
        self.safety_check = safety_check

        try:
            # Add timeout to prevent infinite running
            return await asyncio.wait_for(
                self._execute_workflow(query, budget_amount, currency),
                timeout=300.0  # 5 minutes timeout
            )
        except asyncio.TimeoutError:
            print("⏰ [WORKFLOW] Workflow timed out after 5 minutes")
            return "Error: Trip planning timed out. Please try again with a simpler request."
        except Exception as e:
            print(f"❌ [WORKFLOW] Unexpected error: {str(e)}")
            return f"Error: {str(e)}"

    async def _execute_workflow(self, query: str, budget_amount: float | None = None, currency: str = "USD") -> str:
        """Execute the actual workflow logic"""
        try:
            # Step 1: Extract tour information with Gemini
            print("🎯 [WORKFLOW] Step 1: Extracting tour information with Gemini...")
            extracted_info = extract_tour_information(query)
            if not extracted_info.tour_info:
                print(f"❌ [WORKFLOW] Failed to extract tour info: {extracted_info.reasoning}")
                return f"Failed to plan the tour. Possible reason: {extracted_info.reasoning}"

            destination = extracted_info.tour_info.destination
            print(f"✅ [WORKFLOW] Extracted destination: {destination}")

            # Determine trip dates for nights calculation
            start_date = extracted_info.tour_info.departure_date
            end_date = extracted_info.tour_info.return_date
            nights = 0
            try:
                ci_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                co_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                nights = max((co_dt - ci_dt).days, 0)
            except Exception:
                nights = 0

            # Step 2: Flights - prefer Gemini Grounding, then fallback to SerpAPI
            print("[WORKFLOW] Step 2: Finding flights (grounded first)...")

            def has_flight_lines(formatted: str) -> bool:
                if not formatted:
                    return False
                header_ok = formatted.startswith("Flights from ")
                info_ok = ("Price (USD):" in formatted) or ("Total Duration:" in formatted)
                return header_ok and info_ok

            # Only use the user's primary departure airport to avoid jumping to far-away airports
            from_list = [extracted_info.tour_info.airport_from] if extracted_info.tour_info.airport_from else []
            to_list = ([extracted_info.tour_info.airport_to] if extracted_info.tour_info.airport_to else []) + (extracted_info.tour_info.alternative_airports_to or [])
            # Deduplicate while preserving order
            seen = set()
            from_list = [a for a in from_list if not (a in seen or seen.add(a))]
            seen = set()
            to_list = [a for a in to_list if not (a in seen or seen.add(a))]

            # Check if we have valid airports
            if not from_list or not to_list:
                print("[WORKFLOW] No valid airports found, skipping flight search")
                self.flights_data = ""
            else:
                # 2.a Grounded primary
                grounded_found = False
                flights_formatted = ""
                try:
                    finder = GroundedFlightFinder()
                    grounded = await finder.find_flights(
                        from_list[0],
                        to_list[0],
                        extracted_info.tour_info.departure_date,
                        extracted_info.tour_info.return_date,
                    )
                    if has_flight_lines(grounded):
                        flights_formatted = grounded
                        grounded_found = True
                        print("[WORKFLOW] Grounded flight search returned results")
                except Exception as _ge:
                    print(f"[WORKFLOW] Grounded flight search error: {_ge}")

                if grounded_found:
                    # If it's a round-trip, append reverse leg using the same primary airports
                    if extracted_info.tour_info.return_date:
                        try:
                            reverse_text = find_flights(
                                to_list[0],
                                from_list[0],
                                extracted_info.tour_info.return_date,
                                None,
                                currency=currency,
                                avoid_red_eye=self.flight_preferences.avoid_red_eye if self.flight_preferences else False,
                                avoid_early_morning=self.flight_preferences.avoid_early_morning if self.flight_preferences else False,
                                child_friendly=self.flight_preferences.child_friendly if self.flight_preferences else False,
                                senior_friendly=self.flight_preferences.senior_friendly if self.flight_preferences else False,
                                direct_flights_only=self.flight_preferences.direct_flights_only if self.flight_preferences else False,
                            )
                            if has_flight_lines(reverse_text):
                                flights_formatted = f"{flights_formatted}\n\n{reverse_text}"
                        except Exception:
                            pass
                    # Keep only top 3 cheapest for each direction when possible
                    self.flights_data = flights_formatted
                    print("[WORKFLOW] Flights data set from grounded search")
                else:
                    print("[WORKFLOW] Grounded empty; trying SerpAPI...")
                    found = False
                    selected_pair = (None, None)
                    for dep in from_list:
                        if found:
                            break
                        for arr in to_list:
                            try:
                                candidate = find_flights(
                                    dep,
                                    arr,
                                    extracted_info.tour_info.departure_date,
                                    extracted_info.tour_info.return_date,
                                    currency=currency,
                                    avoid_red_eye=self.flight_preferences.avoid_red_eye if self.flight_preferences else False,
                                    avoid_early_morning=self.flight_preferences.avoid_early_morning if self.flight_preferences else False,
                                    child_friendly=self.flight_preferences.child_friendly if self.flight_preferences else False,
                                    senior_friendly=self.flight_preferences.senior_friendly if self.flight_preferences else False,
                                    direct_flights_only=self.flight_preferences.direct_flights_only if self.flight_preferences else False,
                                )
                                if has_flight_lines(candidate):
                                    flights_formatted = candidate
                                    selected_pair = (dep, arr)
                                    found = True
                                    break
                            except Exception:
                                continue
                    if found:
                        # Add a separate return one-way if possible
                        if extracted_info.tour_info.return_date and selected_pair[0] and selected_pair[1]:
                            try:
                                reverse_text = find_flights(
                                    selected_pair[1],
                                    selected_pair[0],
                                    extracted_info.tour_info.return_date,
                                    None,
                                    currency=currency,
                                    avoid_red_eye=self.flight_preferences.avoid_red_eye if self.flight_preferences else False,
                                    avoid_early_morning=self.flight_preferences.avoid_early_morning if self.flight_preferences else False,
                                    child_friendly=self.flight_preferences.child_friendly if self.flight_preferences else False,
                                    senior_friendly=self.flight_preferences.senior_friendly if self.flight_preferences else False,
                                    direct_flights_only=self.flight_preferences.direct_flights_only if self.flight_preferences else False,
                                )
                                if has_flight_lines(reverse_text):
                                    flights_formatted = f"{flights_formatted}\n\n{reverse_text}"
                            except Exception:
                                pass
                        self.flights_data = flights_formatted
                        print(f"[WORKFLOW] Flights data retrieved via SerpAPI for {selected_pair[0]} -> {selected_pair[1]}")
                    else:
                        self.flights_data = ""
                        print("[WORKFLOW] No flights found from grounded or SerpAPI")

            # Step 3: Find hotels
            print("🏨 [WORKFLOW] Step 3: Finding hotels...")
            _check_in = extracted_info.tour_info.departure_date
            _check_out = extracted_info.tour_info.return_date
            try:
                ci_dt = datetime.strptime(_check_in, "%Y-%m-%d").date()
                co_dt = datetime.strptime(_check_out, "%Y-%m-%d").date()
                if co_dt <= ci_dt:
                    co_dt = ci_dt + timedelta(days=3)
                    _check_out = co_dt.strftime("%Y-%m-%d")
            except Exception:
                pass
            # Enforce hotel budget cap if budget present
            remaining_currency = (currency or "USD").upper()
            self.hotels_data = find_hotels(
                extracted_info.tour_info.destination,
                _check_in,
                _check_out,
                currency=currency,
                toddler_friendly=self.consider_toddler_friendly,
                senior_friendly=self.consider_senior_friendly,
            )
            if budget_amount is not None and budget_amount > 0:
                try:
                    import re as _re
                    # Estimate flight min cost to compute remaining for hotels
                    min_flight = 0.0
                    if self.flights_data:
                        patt = rf"Price \({remaining_currency}\): [\$₹]?([0-9]+)"
                        vals = [float(v) for v in _re.findall(patt, self.flights_data or "")]
                        if vals:
                            # Outbound and return may be present; sum the minimum from each section if detectable.
                            # Fallback: use overall minimum if sections aren't clearly separated.
                            min_flight = sum(sorted(vals)[:2]) if len(vals) >= 2 else min(vals)

                    # Compute nights
                    nights_cap = 0
                    try:
                        ci_dt = datetime.strptime(_check_in, "%Y-%m-%d").date()
                        co_dt = datetime.strptime(_check_out, "%Y-%m-%d").date()
                        nights_cap = max((co_dt - ci_dt).days, 1)
                    except Exception:
                        nights_cap = 1

                    remaining_total = max(float(budget_amount) - min_flight, 0.0)
                    per_night_cap = remaining_total / nights_cap if nights_cap else remaining_total

                    # Filter hotel blocks by per-night cap
                    blocks = [b for b in (self.hotels_data.split('\n\n')) if b.strip()]
                    header = blocks[0] if blocks else "Accommodations"
                    hotel_blocks = blocks[1:] if len(blocks) > 1 else []
                    def _rate_num(txt: str) -> float:
                        m = _re.search(r"Rate per night: ([^\n]+)", txt)
                        if not m:
                            return float("inf")
                        raw = m.group(1)
                        mnum = _re.search(r"([0-9]+(?:\.[0-9]+)?)", raw)
                        if not mnum:
                            return float("inf")
                        try:
                            return float(mnum.group(1))
                        except Exception:
                            return float("inf")

                    within_cap = [hb for hb in hotel_blocks if _rate_num(hb) <= per_night_cap]
                    if within_cap:
                        # Keep at most 3 within cap
                        within_cap.sort(key=_rate_num)
                        self.hotels_data = header + "\n\n" + "\n\n".join(within_cap[:3]) + "\n"
                except Exception:
                    pass
            print(f"✅ [WORKFLOW] Hotels data retrieved")

            # Step 4: Find places to visit
            print("📍 [WORKFLOW] Step 4: Finding places...")
            try:
                self.places_data = find_places_to_visit(
                    destination, 
                    toddler_friendly=self.consider_toddler_friendly,
                    senior_friendly=self.consider_senior_friendly
                )
                print(f"✅ [WORKFLOW] Places data retrieved: {len(self.places_data) if self.places_data else 0} characters")
            except Exception as e:
                print(f"❌ [WORKFLOW] Error finding places: {str(e)}")
                # Create fallback places data
                self.places_data = f"Here are the top places to visit in {destination}:\n\n"
                self.places_data += f"{destination} City Center\n"
                self.places_data += "Description: Explore the vibrant heart of the city\n"
                self.places_data += "Rating: 4.2 (Popular destination)\n"
                self.places_data += "Price: Free Entry\n"
                self.places_data += "Image: N/A\n\n"
                self.places_data += f"{destination} Historic Area\n"
                self.places_data += "Description: Discover local history and architecture\n"
                self.places_data += "Rating: 4.3 (Historical significance)\n"
                self.places_data += "Price: Free Entry\n"
                self.places_data += "Image: N/A\n\n"
                self.places_data += f"Local Attractions\n"
                self.places_data += "Description: Popular local sights and activities\n"
                self.places_data += "Rating: 4.0 (Various options)\n"
                self.places_data += "Price: Varies\n"
                self.places_data += "Image: N/A\n"
                print(f"✅ [WORKFLOW] Created fallback places data")

            # Step 5: Generate itinerary using Gemini
            print("📄 [WORKFLOW] Step 5: Generating itinerary with Gemini...")

            # Budget-aware context preparation (no currency conversion; API returns desired currency)
            budget_summary_note = ""
            user_currency = (currency or "USD").upper()
            if budget_amount is not None and budget_amount > 0:
                try:
                    import re as _re
                    # Flight costs: choose minimum available in user currency
                    flight_cost = 0.0
                    if self.flights_data:
                        patt = rf"Price \({user_currency}\): [\$₹]?([0-9]+)"
                        vals = [float(v) for v in _re.findall(patt, self.flights_data or "")]
                        if vals:
                            flight_cost = min(vals)

                    # Hotels: first available nightly rate in the text
                    nightly = 0.0
                    if self.hotels_data:
                        m2 = _re.search(r"Rate per night: ([^\n]+)", self.hotels_data)
                        if m2:
                            raw = m2.group(1).strip()
                            mnum = _re.search(r"([0-9]+(?:\.[0-9]+)?)", raw)
                            if mnum:
                                nightly = float(mnum.group(1))

                    total_hotel = nightly * max(nights, 1)
                    est_total = flight_cost + total_hotel
                    overage = max(est_total - float(budget_amount), 0.0)
                    symbol = "$" if user_currency == "USD" else "₹"
                    budget_summary_note = (
                        f"Budget: {symbol}{float(budget_amount):,.0f} {user_currency}. "
                        f"Estimated total (flights + hotels): {symbol}{est_total:,.0f} {user_currency}. "
                        + (f"Over budget by {symbol}{overage:,.0f}. " if overage > 0 else "Within budget. ")
                    )
                except Exception:
                    budget_summary_note = f"Budget: {budget_amount} {user_currency}. (Estimation unavailable)"

            # Prepare traveler context for itinerary
            traveler_context = ""
            if self.travelers:
                traveler_context = f"\n\nTraveler Information:\n"
                traveler_context += f"- Adults: {self.travelers.adults}\n"
                traveler_context += f"- Children: {self.travelers.children}\n"
                traveler_context += f"- Seniors: {self.travelers.seniors}\n"
                traveler_context += f"- Children under 5: {self.travelers.children_under_5}\n"
                if self.travelers.itinerary_based_passengers:
                    traveler_context += f"- Itinerary should be tailored to passenger types\n"

            # Add special considerations
            special_considerations = ""
            if self.consider_toddler_friendly:
                special_considerations += "\n- Include toddler-friendly activities and accommodations\n"
            if self.consider_senior_friendly:
                special_considerations += "\n- Include senior citizen-friendly activities and accommodations\n"

            # Add flight preferences context
            flight_prefs_context = ""
            if self.flight_preferences:
                flight_prefs_context = "\n\nFlight Preferences:\n"
                if self.flight_preferences.avoid_red_eye:
                    flight_prefs_context += "- Avoid red-eye flights\n"
                if self.flight_preferences.avoid_early_morning:
                    flight_prefs_context += "- Avoid early morning flights (before 8 AM)\n"
                if self.flight_preferences.child_friendly:
                    flight_prefs_context += "- Prefer child-friendly flight times\n"
                if self.flight_preferences.senior_friendly:
                    flight_prefs_context += "- Prefer senior-friendly flight times\n"
                if self.flight_preferences.direct_flights_only:
                    flight_prefs_context += "- Prefer direct flights only\n"

            # Add safety information if requested
            safety_context = ""
            if self.safety_check:
                safety_context = "\n\nSafety Information:\n- Consider travel safety and current conditions\n- Provide safety tips for the destination\n"

            self.itinerary = write_itinerary(
                query,
                destination,
                flights_info=self.flights_data,
                hotels_info=self.hotels_data,
                sights_info=(self.places_data + ("\n\n" + budget_summary_note if budget_summary_note else "") + 
                           traveler_context + special_considerations + flight_prefs_context + safety_context),
                language=self.language,
            )
            print(f"✅ [WORKFLOW] Itinerary generated")

            # Generate PDF from the markdown itinerary
            print("📄 [WORKFLOW] Converting itinerary to PDF...")
            pdf_base64 = await self._generate_pdf_from_markdown(self.itinerary)
            print(f"✅ [WORKFLOW] PDF generated successfully")
            print(f"📊 [WORKFLOW] PDF data length: {len(pdf_base64)} characters")
            print(f"🎯 [WORKFLOW] PDF data ready for download")

            return pdf_base64

        except Exception as e:
            print(f"❌ [WORKFLOW] Error: {str(e)}")
            return f"Error occurred during trip planning: {str(e)}"

    async def _generate_pdf_from_markdown(self, markdown_content: str) -> str:
        """Generate comprehensive PDF with itinerary, flights, hotels, and places data"""
        try:
            print("📄 [PDF-GEN] Starting comprehensive PDF generation...")

            # Generate HTML content with all travel data
            html_content = self._create_complete_html_content(markdown_content)
            
            # Generate temporary filename using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_file = os.path.join(tempfile.gettempdir(), f"itinerary_{timestamp}.pdf")
            print(f"📝 [PDF-GEN] Creating PDF file: {pdf_file}")

            # Try using xhtml2pdf first (more reliable than wkhtmltopdf)
            try:
                from xhtml2pdf import pisa
                print("✅ [PDF-GEN] Using xhtml2pdf for PDF generation")
                
                with open(pdf_file, 'wb') as output_file:
                    pisa_status = pisa.CreatePDF(html_content, dest=output_file)
                
                if pisa_status.err:
                    print(f"⚠️ [PDF-GEN] xhtml2pdf warnings: {pisa_status.err}")
                
                if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 1000:
                    print("✅ [PDF-GEN] PDF generated successfully with xhtml2pdf")
                else:
                    raise RuntimeError("xhtml2pdf generated invalid or empty PDF")
                    
            except Exception as xhtml_error:
                print(f"❌ [PDF-GEN] xhtml2pdf failed: {str(xhtml_error)}")
                
                # Fallback to pdfkit if available
                try:
                    import pdfkit
                    print("🔄 [PDF-GEN] Falling back to pdfkit...")
                    
                    options = {
                        'encoding': 'UTF-8',
                        'enable-local-file-access': None,
                        'margin-top': '20mm',
                        'margin-right': '20mm',
                        'margin-bottom': '20mm',
                        'margin-left': '20mm',
                        'no-outline': None,
                        'quiet': ''
                    }
                    
                    pdfkit.from_string(html_content, pdf_file, options=options)
                    print("✅ [PDF-GEN] PDF generated successfully with pdfkit")
                    
                except Exception as pdfkit_error:
                    print(f"❌ [PDF-GEN] pdfkit also failed: {str(pdfkit_error)}")
                    return self._fallback_markdown_download(markdown_content)

            # Verify PDF was created successfully
            if not os.path.exists(pdf_file):
                print("❌ [PDF-GEN] PDF file was not created")
                return self._fallback_markdown_download(markdown_content)

            file_size = os.path.getsize(pdf_file)
            print(f"📊 [PDF-GEN] PDF file size: {file_size} bytes")

            if file_size < 1000:
                print("❌ [PDF-GEN] PDF file is too small, likely corrupted")
                return self._fallback_markdown_download(markdown_content)

            # Read PDF file and convert to base64
            print("📖 [PDF-GEN] Reading PDF file...")
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()

            print(f"🔄 [PDF-GEN] Converting {len(pdf_data)} bytes to base64...")
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            print(f"✅ [PDF-GEN] PDF converted to base64 ({len(pdf_base64)} characters)")

            # Clean up temporary file
            try:
                os.unlink(pdf_file)
                print("🧹 [PDF-GEN] Temporary file cleaned up")
            except Exception as cleanup_error:
                print(f"⚠️ [PDF-GEN] Cleanup warning: {str(cleanup_error)}")

            print("✅ [PDF-GEN] PDF generation completed successfully")
            return pdf_base64

        except Exception as e:
            print(f"❌ [PDF-GEN] Unexpected error in PDF generation: {str(e)}")
            import traceback
            print(f"❌ [PDF-GEN] Traceback: {traceback.format_exc()}")
            return self._fallback_markdown_download(markdown_content)

    def _create_complete_html_content(self, itinerary_content: str) -> str:
        """Create comprehensive HTML content with all travel data"""
        try:
            print("🎨 [PDF-GEN] Creating comprehensive HTML content...")
            
            # Convert markdown itinerary to HTML
            try:
                import markdown
                itinerary_html = markdown.markdown(itinerary_content, extensions=['tables', 'fenced_code'])
            except ImportError:
                # Fallback: simple markdown to HTML conversion
                itinerary_html = itinerary_content.replace('\n', '<br>')
            
            # Create comprehensive HTML document
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Travel Itinerary - Journezy Trip Planner</title>
                <style>
                    @page {{
                        margin: 12mm;
                        size: A4;
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.3;
                        margin: 0;
                        padding: 0;
                        color: #2d3748;
                        background: #fff;
                        font-size: 11px;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 15px;
                        padding: 12px 0;
                        background: linear-gradient(135deg, #4299e1, #667eea);
                        color: white;
                        border-radius: 6px;
                    }}
                    .header h1 {{
                        font-size: 20px;
                        margin: 0;
                        font-weight: 700;
                    }}
                    .header .subtitle {{
                        font-size: 11px;
                        margin-top: 4px;
                        opacity: 0.9;
                        font-weight: 300;
                    }}
                    .section {{
                        margin-bottom: 10px;
                        page-break-inside: avoid;
                        background: white;
                        border: 1px solid #e2e8f0;
                        border-radius: 4px;
                        padding: 8px;
                    }}
                    .section-title {{
                        background: #4299e1;
                        color: white;
                        padding: 6px 10px;
                        margin: -8px -8px 8px -8px;
                        font-size: 13px;
                        font-weight: 600;
                        border-radius: 4px 4px 0 0;
                    }}
                    .itinerary-content {{
                        background: #f8fafc;
                        padding: 8px;
                        border-radius: 3px;
                        border-left: 3px solid #4299e1;
                        font-size: 10px;
                        line-height: 1.3;
                    }}
                    .flight-item, .hotel-item, .place-item {{
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 4px;
                        padding: 6px;
                        margin-bottom: 6px;
                        border-left: 3px solid #4299e1;
                    }}
                    .flight-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 15px;
                        padding-bottom: 10px;
                        border-bottom: 1px solid #e2e8f0;
                    }}
                    .flight-route {{
                        background: #f7fafc;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 0;
                        text-align: center;
                    }}
                    .route-info {{
                        font-weight: 600;
                        color: #2b6cb0;
                        margin-bottom: 5px;
                    }}
                    .duration-info {{
                        color: #4a5568;
                        font-size: 14px;
                    }}
                    .price-tag {{
                        background: linear-gradient(135deg, #4299e1, #667eea);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: 600;
                        font-size: 16px;
                    }}
                    .item-title {{
                        font-size: 12px;
                        font-weight: 600;
                        color: #2b6cb0;
                        margin-bottom: 4px;
                        line-height: 1.2;
                    }}
                    .item-details {{
                        font-size: 10px;
                        color: #4a5568;
                        line-height: 1.3;
                    }}
                    .detail-item {{
                        margin-bottom: 2px;
                        display: block;
                    }}
                    .detail-item .icon {{
                        margin-right: 3px;
                        color: #4299e1;
                        font-size: 9px;
                    }}
                    .amenities {{
                        margin-top: 4px;
                    }}
                    .amenity {{
                        display: inline-block;
                        background: #e6fffa;
                        padding: 1px 4px;
                        border-radius: 3px;
                        font-size: 8px;
                        color: #234e52;
                        margin: 1px 2px 1px 0;
                    }}
                    .footer {{
                        margin-top: 15px;
                        text-align: center;
                        color: #718096;
                        font-size: 9px;
                        border-top: 1px solid #e2e8f0;
                        padding-top: 8px;
                    }}
                    .no-data {{
                        text-align: center;
                        color: #a0aec0;
                        font-style: italic;
                        padding: 30px;
                        background: #f7fafc;
                        border-radius: 8px;
                        border: 2px dashed #e2e8f0;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2b6cb0;
                        margin: 6px 0 3px 0;
                        font-weight: 600;
                        line-height: 1.2;
                    }}
                    h1 {{ font-size: 16px; }}
                    h2 {{ font-size: 14px; }}
                    h3 {{ font-size: 12px; }}
                    h4 {{ font-size: 11px; }}
                    ul, ol {{
                        padding-left: 12px;
                        margin: 3px 0;
                    }}
                    li {{
                        margin-bottom: 2px;
                        color: #4a5568;
                        font-size: 10px;
                        line-height: 1.3;
                    }}
                    p {{
                        margin: 3px 0;
                        color: #4a5568;
                        font-size: 10px;
                        line-height: 1.3;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 15px 0;
                        background: white;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    }}
                    table th, table td {{
                        border: 1px solid #e2e8f0;
                        padding: 12px 15px;
                        text-align: left;
                    }}
                    table th {{
                        background: linear-gradient(135deg, #4299e1, #667eea);
                        color: white;
                        font-weight: 600;
                        font-size: 14px;
                    }}
                    table td {{
                        background: #f7fafc;
                        color: #4a5568;
                    }}
                    .page-break {{
                        page-break-before: always;
                    }}
                    blockquote {{
                        border-left: 4px solid #4299e1;
                        padding-left: 20px;
                        margin: 20px 0;
                        font-style: italic;
                        color: #4a5568;
                        background: #f7fafc;
                        padding: 15px 20px;
                        border-radius: 0 8px 8px 0;
                    }}
                    code {{
                        background: #edf2f7;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        color: #2d3748;
                    }}
                    pre {{
                        background: #edf2f7;
                        padding: 15px;
                        border-radius: 8px;
                        overflow-x: auto;
                        border-left: 2px solid #4299e1;
                        font-size: 9px;
                        margin: 3px 0;
                    }}
                    .place-image {{
                        max-width: 80px;
                        height: auto;
                        border-radius: 3px;
                        margin: 2px 6px 2px 0;
                        float: right;
                    }}
                    .place-image-section {{
                        clear: both;
                        margin: 4px 0;
                    }}
                    .compact-list {{
                        margin: 0;
                        padding: 0;
                    }}
                    .compact-list li {{
                        margin-bottom: 1px;
                        font-size: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>✈️ Your Perfect Travel Itinerary</h1>
                    <div class="subtitle">Crafted with AI by Journezy Trip Planner</div>
                    <div class="subtitle" style="margin-top: 5px; font-size: 14px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
                </div>

                <div class="section">
                    <h2 class="section-title">📋 Complete Itinerary</h2>
                    <div class="itinerary-content">
                        {itinerary_html}
                    </div>
                </div>

                {self._generate_flights_html()}
                
                {self._generate_hotels_html()}
                
                {self._generate_places_html()}

                <div class="footer">
                    <p>This itinerary was generated by <strong>Journezy Trip Planner</strong></p>
                    <p>AI-powered travel planning with real-time data • Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
            
            print("✅ [PDF-GEN] HTML content created successfully")
            return html_content
            
        except Exception as e:
            print(f"❌ [PDF-GEN] Error creating HTML content: {str(e)}")
            # Fallback to simple HTML
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Travel Itinerary</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    h1 {{ color: #1E3A8A; }}
                </style>
            </head>
            <body>
                <h1>Travel Itinerary</h1>
                <div>{itinerary_content.replace(chr(10), '<br>')}</div>
                <p><em>Generated by Journezy Trip Planner on {datetime.now().strftime('%Y-%m-%d')}</em></p>
            </body>
            </html>
            """

    def _generate_flights_html(self) -> str:
        """Generate HTML for flights section"""
        if not self.flights_data or self.flights_data.strip() == "":
            return '<div class="section"><h2 class="section-title">✈️ Flights</h2><div class="no-data">No flight information available</div></div>'
        
        flights_html = '<div class="section page-break"><h2 class="section-title">✈️ Flights</h2>'
        
        try:
            # Parse flight data
            lines = self.flights_data.split('\n')
            current_flight = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_flight:
                        flights_html += self._format_flight_html(current_flight)
                        current_flight = {}
                elif ' - ' in line and ('→' in line or '->' in line):
                    if current_flight:
                        flights_html += self._format_flight_html(current_flight)
                    current_flight = {'route': line}
                elif line.startswith('Price'):
                    current_flight['price'] = line
                elif line.startswith('Duration') or line.startswith('Total Duration'):
                    current_flight['duration'] = line
            
            if current_flight:
                flights_html += self._format_flight_html(current_flight)
                
        except Exception as e:
            print(f"⚠️ [PDF-GEN] Error parsing flights: {str(e)}")
            flights_html += f'<div class="flight-item"><pre>{self.flights_data}</pre></div>'
        
        flights_html += '</div>'
        return flights_html

    def _format_flight_html(self, flight_data: dict) -> str:
        """Format individual flight data as HTML"""
        return f"""
        <div class="flight-item">
            <div class="item-title">{flight_data.get('route', 'Flight Information')}</div>
            <div class="item-details">
                {f'<div class="detail-item"><span class="icon">💰</span>{flight_data["price"]}</div>' if 'price' in flight_data else ''}
                {f'<div class="detail-item"><span class="icon">⏱️</span>{flight_data["duration"]}</div>' if 'duration' in flight_data else ''}
            </div>
        </div>
        """

    def _generate_hotels_html(self) -> str:
        """Generate HTML for hotels section"""
        if not self.hotels_data or self.hotels_data.strip() == "":
            return '<div class="section"><h2 class="section-title">🏨 Hotels</h2><div class="no-data">No hotel information available</div></div>'
        
        hotels_html = '<div class="section page-break"><h2 class="section-title">🏨 Hotels</h2>'
        
        try:
            # Parse hotel blocks
            hotel_blocks = self.hotels_data.split('\n\n')[1:]  # Skip header
            
            for hotel_block in hotel_blocks:
                if hotel_block.strip():
                    hotels_html += self._format_hotel_html(hotel_block)
                    
        except Exception as e:
            print(f"⚠️ [PDF-GEN] Error parsing hotels: {str(e)}")
            hotels_html += f'<div class="hotel-item"><pre>{self.hotels_data}</pre></div>'
        
        hotels_html += '</div>'
        return hotels_html

    def _format_hotel_html(self, hotel_block: str) -> str:
        """Format individual hotel data as HTML"""
        lines = hotel_block.split('\n')
        hotel_name = lines[0] if lines else 'Hotel'
        
        details = []
        amenities = []
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('Rate per night:'):
                details.append(f'<div class="detail-item"><span class="icon">💰</span>{line}</div>')
            elif line.startswith('Rating:'):
                details.append(f'<div class="detail-item"><span class="icon">⭐</span>{line}</div>')
            elif line.startswith('Location Rating:'):
                details.append(f'<div class="detail-item"><span class="icon">📍</span>{line}</div>')
            elif line.startswith('Amenities:'):
                amenity_list = line.replace('Amenities:', '').split(',')
                amenities = [f'<span class="amenity">{a.strip()}</span>' for a in amenity_list if a.strip()]
        
        amenities_html = f'<div class="amenities">{"".join(amenities)}</div>' if amenities else ''
        
        return f"""
        <div class="hotel-item">
            <div class="item-title">{hotel_name}</div>
            <div class="item-details">
                {"".join(details)}
            </div>
            {amenities_html}
        </div>
        """

    def _generate_places_html(self) -> str:
        """Generate HTML for places section"""
        if not self.places_data or self.places_data.strip() == "":
            return '<div class="section"><h2 class="section-title">📍 Places to Visit</h2><div class="no-data">No places information available</div></div>'
        
        places_html = '<div class="section page-break"><h2 class="section-title">📍 Places to Visit</h2>'
        
        try:
            # Parse places data
            lines = self.places_data.split('\n')
            current_place = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_place:
                        places_html += self._format_place_html(current_place)
                        current_place = {}
                elif line.startswith('Description:'):
                    current_place['description'] = line.replace('Description:', '').strip()
                elif line.startswith('Rating:'):
                    current_place['rating'] = line
                elif line.startswith('Price:'):
                    current_place['price'] = line
                elif not line.startswith('Here are') and not line.startswith('Image:') and not current_place.get('name'):
                    current_place['name'] = line
            
            if current_place:
                places_html += self._format_place_html(current_place)
                
        except Exception as e:
            print(f"⚠️ [PDF-GEN] Error parsing places: {str(e)}")
            places_html += f'<div class="place-item"><pre>{self.places_data}</pre></div>'
        
        places_html += '</div>'
        return places_html

    def _format_place_html(self, place_data: dict) -> str:
        """Format individual place data as HTML"""
        # Include image if available
        image_html = ""
        if 'image' in place_data and place_data['image'] and place_data['image'] != 'N/A':
            image_html = f"""
            <div class="place-image-section">
                <img src="{place_data['image']}" alt="{place_data.get('name', 'Place')}" 
                     style="max-width: 200px; max-height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;" 
                     onerror="this.style.display='none';">
            </div>
            """
        
        return f"""
        <div class="place-item">
            <div class="place-header">
                <div class="item-title">📍 {place_data.get('name', 'Attraction')}</div>
                {f'<div class="place-price-tag">{place_data["price"]}</div>' if 'price' in place_data and place_data["price"] != 'N/A' else ''}
            </div>
            {image_html}
            <div class="item-details">
                {f'<div class="detail-item"><i class="fas fa-info-circle" style="color: #10b981; margin-right: 5px;"></i>{place_data["description"]}</div>' if 'description' in place_data and place_data["description"] != 'N/A' else ''}
                {f'<div class="detail-item"><i class="fas fa-star" style="color: #f59e0b; margin-right: 5px;"></i>{place_data["rating"]}</div>' if 'rating' in place_data and place_data["rating"] != 'N/A' else ''}
            </div>
        </div>
        """

    def _fallback_markdown_download(self, markdown_content: str) -> str:
        """Fallback to markdown download when PDF generation fails"""
        print("🔄 [PDF-GEN] Using markdown fallback")
        try:
            markdown_base64 = base64.b64encode(markdown_content.encode('utf-8')).decode('utf-8')
            print(f"✅ [PDF-GEN] Markdown fallback ready ({len(markdown_base64)} characters)")
            return markdown_base64
        except Exception as fallback_error:
            print(f"❌ [PDF-GEN] Markdown fallback failed: {str(fallback_error)}")
            return ""