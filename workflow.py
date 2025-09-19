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
        self.itinerary_first = False
        self.consider_toddler_friendly = False
        self.consider_senior_friendly = False
        self.safety_check = True

    async def run(self, query: str, *, budget_amount: float | None = None, currency: str = "USD", 
                  travelers=None, flight_preferences=None, itinerary_first: bool = False,
                  consider_toddler_friendly: bool = False, consider_senior_friendly: bool = False,
                  safety_check: bool = True) -> str:
        """Main workflow execution using Gemini directly"""
        print("🤖 [WORKFLOW] Starting workflow...")
        print(f"📝 [WORKFLOW] Query: {query}")

        # Store the new parameters
        self.travelers = travelers
        self.flight_preferences = flight_preferences
        self.itinerary_first = itinerary_first
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
            # Skip flights if itinerary-first is enabled
            if self.itinerary_first:
                print("[WORKFLOW] Step 2: Skipping flights (itinerary-first mode)...")
                self.flights_data = ""
            else:
                print("[WORKFLOW] Step 2: Finding flights (grounded first)...")

                def has_flight_lines(formatted: str) -> bool:
                    if not formatted:
                        return False
                    header_ok = formatted.startswith("Flights from ")
                    info_ok = ("Price (USD):" in formatted) or ("Total Duration:" in formatted)
                    return header_ok and info_ok

                # Only use the user's primary departure airport to avoid jumping to far-away airports
                from_list = [extracted_info.tour_info.airport_from]
                to_list = [extracted_info.tour_info.airport_to] + (extracted_info.tour_info.alternative_airports_to or [])
                # Deduplicate while preserving order
                seen = set()
                from_list = [a for a in from_list if not (a in seen or seen.add(a))]
                seen = set()
                to_list = [a for a in to_list if not (a in seen or seen.add(a))]

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
            self.places_data = find_places_to_visit(
                destination, 
                toddler_friendly=self.consider_toddler_friendly,
                senior_friendly=self.consider_senior_friendly
            )
            print(f"✅ [WORKFLOW] Places data retrieved")

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
            if self.itinerary_first:
                special_considerations += "\n- Prioritize itinerary planning over flight selection\n"

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
        """Convert markdown content to PDF and return as base64"""
        try:
            print("📄 [PDF-GEN] Starting PDF generation process...")

            # Check if wkhtmltopdf is available
            try:
                import pdfkit
                config = pdfkit.configuration()
                print(f"✅ [PDF-GEN] wkhtmltopdf found at: {config.wkhtmltopdf}")
            except Exception as wkhtml_error:
                print(f"❌ [PDF-GEN] wkhtmltopdf not found: {str(wkhtml_error)}")
                print("🔄 [PDF-GEN] Falling back to markdown download")
                return self._fallback_markdown_download(markdown_content)

            # Generate temporary filenames using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_file = os.path.join(tempfile.gettempdir(), f"itinerary_{timestamp}.md")
            pdf_file = os.path.join(tempfile.gettempdir(), f"itinerary_{timestamp}.pdf")

            print(f"📝 [PDF-GEN] Creating temporary files: {md_file}, {pdf_file}")

            # Write markdown file
            with open(md_file, "w", encoding='utf-8') as f:
                f.write(markdown_content)
            print("✅ [PDF-GEN] Markdown file written")

            # Convert markdown to HTML
            try:
                html_content = gh_md_to_html.markdown_to_html_via_github_api(markdown_content)
                print("✅ [PDF-GEN] Markdown converted to HTML")
            except Exception as html_error:
                print(f"❌ [PDF-GEN] HTML conversion failed: {str(html_error)}")
                return self._fallback_markdown_download(markdown_content)

            # Create HTML template
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        direction: ltr;
                        line-height: 1.6;
                        margin: 2em;
                        font-size: 14px;
                    }}
                    h1, h2, h3 {{ margin-top: 1em; }}
                    .content {{ max-width: 800px; margin: 0 auto; }}
                    img {{ max-width: 100%; height: auto; }}
                    pre {{ white-space: pre-wrap; }}
                    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
                </style>
            </head>
            <body>
                <div class="content">
                    {html_content}
                </div>
            </body>
            </html>
            """

            print("🎨 [PDF-GEN] HTML template created")

            # Configure pdfkit options
            options = {{
                'encoding': 'UTF-8',
                'enable-local-file-access': None,
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'custom-header': [('Accept-Encoding', 'gzip')],
                'no-outline': None,
                'quiet': ''
            }}

            # Generate PDF
            try:
                pdfkit.from_string(html_template, pdf_file, options=options)
                print("✅ [PDF-GEN] PDF generated successfully")
            except Exception as pdf_error:
                print(f"❌ [PDF-GEN] PDF generation failed: {str(pdf_error)}")
                # Hard fallback to xhtml2pdf to always return a PDF
                try:
                    from xhtml2pdf import pisa
                    # Use the same HTML we built
                    with open(pdf_file, 'wb') as outf:
                        pisa.CreatePDF(html_template, dest=outf)
                    if not os.path.exists(pdf_file) or os.path.getsize(pdf_file) < 1000:
                        raise RuntimeError("xhtml2pdf produced an invalid PDF")
                except Exception as e2:
                    print(f"❌ [PDF-GEN] xhtml2pdf fallback failed: {e2}")
                    raise

            # Check if PDF file was created and has content
            if not os.path.exists(pdf_file):
                print("❌ [PDF-GEN] PDF file was not created")
                # Last resort: try xhtml2pdf as well
                try:
                    from xhtml2pdf import pisa
                    with open(pdf_file, 'wb') as outf:
                        pisa.CreatePDF(html_template, dest=outf)
                    if not os.path.exists(pdf_file) or os.path.getsize(pdf_file) < 1000:
                        raise RuntimeError("xhtml2pdf produced an invalid PDF")
                except Exception as e3:
                    print(f"❌ [PDF-GEN] xhtml2pdf fallback (size check) failed: {e3}")
                    return self._fallback_markdown_download(markdown_content)

            file_size = os.path.getsize(pdf_file)
            print(f"📊 [PDF-GEN] PDF file size: {file_size} bytes")

            if file_size < 1000:  # PDF should be at least 1KB
                print("❌ [PDF-GEN] PDF file is too small, likely corrupted")
                return self._fallback_markdown_download(markdown_content)

            # Read PDF file and convert to base64
            print("📖 [PDF-GEN] Reading PDF file...")
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()

            print(f"🔄 [PDF-GEN] Converting {len(pdf_data)} bytes to base64...")
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            print(f"✅ [PDF-GEN] PDF converted to base64 ({len(pdf_base64)} characters)")

            # Clean up temporary files
            try:
                os.unlink(md_file)
                os.unlink(pdf_file)
                print("🧹 [PDF-GEN] Temporary files cleaned up")
            except Exception as cleanup_error:
                print(f"⚠️ [PDF-GEN] Cleanup warning: {str(cleanup_error)}")

            print("✅ [PDF-GEN] PDF generation completed successfully")
            print(f"🎯 [PDF-GEN] Ready for download - {len(pdf_base64)} characters of base64 data")
            return pdf_base64

        except Exception as e:
            print(f"❌ [PDF-GEN] Unexpected error in PDF generation: {str(e)}")
            return self._fallback_markdown_download(markdown_content)

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