import os
import asyncio
from typing import Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from loguru import logger

try:
    # New Google GenAI client (for grounding)
    from google import genai
    from google.genai import types
except Exception as _e:  # pragma: no cover
    genai = None
    types = None

load_dotenv()


class GroundedFlightsSummarizer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        if genai is None:
            raise RuntimeError("google-genai package not available")
        self.client = genai.Client(api_key=api_key)
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        self.config = types.GenerateContentConfig(tools=[self.grounding_tool])

    async def summarize_flights(self, query: str, flights_text: str) -> Dict[str, Any]:
        """Use Gemini Grounding to provide a grounded summary/citations for flight options."""
        if not flights_text:
            return {"text": "No flights found for this route.", "citations": []}

        prompt = (
            f"Given the user query: {query}\n\n"
            f"Here are the flight options text (verbatim):\n{flights_text}\n\n"
            "Summarize key options (cheapest, fastest, fewest stops) with prices and durations strictly based on the provided text. "
            "Add concise guidance (1-2 lines)."
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=self.config,
            )
            text = response.text or ""
            grounding = response.candidates[0].grounding_metadata if response.candidates else None
            citations = []
            if grounding and hasattr(grounding, "grounding_supports") and grounding.grounding_supports:
                chunks = getattr(grounding, "grounding_chunks", [])
                for sup in grounding.grounding_supports:
                    if getattr(sup, "grounding_chunk_indices", None):
                        for i in sup.grounding_chunk_indices:
                            if i < len(chunks) and getattr(chunks[i], "web", None) and getattr(chunks[i].web, "uri", None):
                                citations.append(chunks[i].web.uri)
            return {"text": text, "citations": citations}
        except Exception as e:
            logger.error(f"Grounded summary error: {e}")
            return {"text": "Grounded summary unavailable.", "citations": []}



class GroundedFlightFinder:
    """Fallback flight finder using Gemini Grounding when SerpAPI returns no results."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        if genai is None:
            raise RuntimeError("google-genai package not available")
        self.client = genai.Client(api_key=api_key)
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        self.config = types.GenerateContentConfig(tools=[self.grounding_tool])

    async def find_flights(self, dep: str, arr: str, depart_date: str, return_date: str | None) -> str:
        """
        Use grounded search to retrieve top 3 options for outbound (and return if provided).
        Returns a text formatted exactly like tools/flights.get_formatted_flights_info expects.
        """
        search_query = (
            f"Find commercial flight options for {dep} to {arr} on {depart_date}"
            + (f" and return on {return_date}" if return_date else "")
            + ". Use reliable sources (Google Flights, airline sites)."
            " Return STRICT JSON with keys: outbound (array of options), return (array of options, optional)."
            " Each option must have: price_usd (number), total_duration_min (number),"
            " flights (array of segments with: flight_number, airline, departure_airport{id,time}, arrival_airport{id,time}, duration_min, airplane),"
            " and layovers (array with id and duration_min)."
            " Output ONLY JSON."
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash-lite",
                contents=search_query,
                config=self.config,
            )
            text = (response.text or "").strip()
        except Exception as e:
            logger.error(f"Grounded flight fetch error: {e}")
            return ""

        import json as _json
        import re as _re

        try:
            data = _json.loads(text)
        except Exception:
            m = _re.search(r"\{[\s\S]*\}", text)
            if not m:
                return ""
            try:
                data = _json.loads(m.group(0))
            except Exception:
                return ""

        outbound = data.get("outbound") or []
        ret = data.get("return") or []

        def _fmt_minutes(total_minutes: int) -> str:
            try:
                total_minutes = int(total_minutes)
            except Exception:
                return ""
            h = total_minutes // 60
            m = total_minutes % 60
            if h > 0 and m > 0:
                return f"{h} hr {m} min"
            if h > 0:
                return f"{h} hr"
            return f"{m} min"

        lines: list[str] = [f"Flights from {dep} to {arr}:", ""]

        def _append_option(option: dict):
            flights = option.get("flights") or []
            for seg in flights:
                airline = seg.get("airline", "")
                flight_no = seg.get("flight_number", "")
                dep_air = seg.get("departure_airport", {}).get("id", "")
                arr_air = seg.get("arrival_airport", {}).get("id", "")
                dep_time = seg.get("departure_airport", {}).get("time", "")
                arr_time = seg.get("arrival_airport", {}).get("time", "")
                duration = _fmt_minutes(seg.get("duration_min", 0))
                airplane = seg.get("airplane", "")
                lines.append(f"{airline} {flight_no} - {dep_air} ({dep_time}) -> {arr_air} ({arr_time}) [{duration}] - {airplane}")
            layovers = option.get("layovers") or []
            if layovers:
                lv = layovers[0]
                lines.append(f"Layover at {lv.get('id','')}: {_fmt_minutes(lv.get('duration_min', 0))}")
            total_dur = _fmt_minutes(option.get("total_duration_min", 0))
            if total_dur:
                lines.append(f"Total Duration: {total_dur}")
            price = option.get("price_usd")
            if price is not None:
                lines.append(f"Price (USD): ${int(price)}")
            lines.append("")

        for opt in outbound[:3]:
            _append_option(opt)

        # If return exists, append a separate section for clarity
        if return_date and ret:
            lines.append(f"Flights from {arr} to {dep}:")
            lines.append("")
            for opt in ret[:3]:
                _append_option(opt)

        output = "\n".join(lines).strip()
        return output


# ======================
# TourInfo extraction via Gemini Grounding (structured + citations)
# ======================

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


def add_citations(response):
    text = response.text
    try:
        supports = response.candidates[0].grounding_metadata.grounding_supports
        chunks = response.candidates[0].grounding_metadata.grounding_chunks
    except Exception:
        return text

    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if getattr(support, "grounding_chunk_indices", None):
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks) and getattr(chunks[i], "web", None) and getattr(chunks[i].web, "uri", None):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text


class GroundedTourExtractor:
    """Extract structured TourInfo using Gemini with Google Search grounding and return citations text."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        if genai is None:
            raise RuntimeError("google-genai package not available")
        self.client = genai.Client(api_key=api_key)
        self.tool = types.Tool(google_search=types.GoogleSearch())
        self.config = types.GenerateContentConfig(
            response_schema=TourInfo,
            tools=[self.tool],
            # response_mime_type could be set to 'application/json' if desired
        )

    async def extract(self, user_query: str) -> dict:
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model="gemini-2.5-flash-lite",
            contents=user_query,
            config=self.config,
        )
        # Structured JSON in response.text by schema; also build citations-annotated text
        structured_json = response.text or ""
        cited_text = add_citations(response)
        return {"structured": structured_json, "cited_text": cited_text}

