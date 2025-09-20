import google.generativeai as genai
import os

ITINERARY_WRITE_PROMPT = """
You're a seasoned travel planner with a knack for finding the best deals and exploring new destinations. You're known for your attention to detail
and your ability to make travel planning easy for customers.

Based on the user's request, flight, hotel and sights information given below, write an itinerary for a customer who is planning a trip to {destination}.
---
{flights_info}
---
{hotels_info}
---
{sights_info}
---
User's request: {query}
---
Language: {language}
---
Please create a detailed itinerary in {language} that:
1. Starts with a brief trip overview including total duration and key highlights
2. Lists all flight details with clear departure/arrival times and layover information
3. Provides accommodation details with check-in/check-out times
4. Creates a day-by-day itinerary that:
   - Accounts for arrival and departure times
   - Groups nearby attractions together to minimize travel time
   - Includes suggested meal times and restaurant recommendations
   - Factors in reasonable travel times between locations
   - Includes estimated costs where available
   - Includes Image links in the itinerary for the sights and hotels
5. Ends with practical tips specific to the destination (local transportation, weather considerations, cultural notes)

Format the itinerary in markdown with clear sections using headers (##) and bullet points. Use bold text (**) for times and important details.
Do not add this line: If you have any questions or need further assistance, feel free to ask.

The full itinerary in markdown following the user's request:
"""


def write_itinerary(
    query: str,
    destination: str,
    flights_info: str,
    hotels_info: str,
    sights_info: str,
    language: str = "english",
) -> str:
    """Generate itinerary using Google Gemini SDK"""
    print("🤖 [GEMINI-ITINERARY] Starting itinerary generation with Gemini...")
    print(f"📍 [GEMINI-ITINERARY] Destination: {destination}")
    print(f"🌐 [GEMINI-ITINERARY] Language: {language}")

    try:
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("No API key found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")

        print("🔑 [GEMINI-ITINERARY] API key configured for Gemini")
        genai.configure(api_key=api_key)

        # Create Gemini model
        model_name = "gemini-2.5-flash-lite"
        model = genai.GenerativeModel(model_name)
        print(f"🎯 [GEMINI-ITINERARY] Using Gemini model: {model_name}")

        # Format the prompt with all the information
        formatted_prompt = ITINERARY_WRITE_PROMPT.format(
            destination=destination,
            flights_info=flights_info,
            hotels_info=hotels_info,
            sights_info=sights_info,
            query=query,
            language=language
        )

        print("📤 [GEMINI-ITINERARY] Sending request to Gemini...")
        print(f"📊 [GEMINI-ITINERARY] Input data sizes - Flights: {len(flights_info)}, Hotels: {len(hotels_info)}, Places: {len(sights_info)}")

        # Use Gemini to generate the itinerary
        response = model.generate_content(formatted_prompt)

        print("✅ [GEMINI-ITINERARY] Response received")
        print(f"📄 [GEMINI-ITINERARY] Generated itinerary length: {len(response.text)} characters")
        print(f"💬 [GEMINI-ITINERARY] Itinerary preview: {response.text[:200]}...")

        # Clean up the response to remove any broken URLs or problematic links
        cleaned_itinerary = clean_itinerary_content(response.text)
        print("🧹 [GEMINI-ITINERARY] Itinerary content cleaned")
        
        # Process the response to convert image links to proper markdown images
        processed_itinerary = process_itinerary_images(cleaned_itinerary, flights_info, hotels_info, sights_info)
        print("🖼️  [GEMINI-ITINERARY] Images processed and embedded in itinerary")

        return processed_itinerary

    except Exception as e:
        print(f"❌ [GEMINI-ITINERARY] Error: {str(e)}")
        return f"Error generating itinerary with Gemini: {str(e)}"


def clean_itinerary_content(itinerary_text: str) -> str:
    """Clean up itinerary content by removing broken URLs and problematic links"""
    import re
    
    # Remove broken Google User Content URLs
    broken_url_patterns = [
        r'https://lh3\.googleusercontent\.com/gps-cs-s/[^\s\)]*',
        r'https://[^\s]*googleusercontent\.com/gps-cs-s/[^\s\)]*',
        r'\[.*?\]\(https://lh3\.googleusercontent\.com/gps-cs-s/[^\)]*\)',
        r'brw-[A-Za-z0-9_-]*',  # Remove broken URL fragments
    ]
    
    cleaned_text = itinerary_text
    for pattern in broken_url_patterns:
        # Remove the broken URLs
        cleaned_text = re.sub(pattern, '', cleaned_text)
        print(f"🧹 [CLEAN-ITINERARY] Removed broken URLs matching pattern: {pattern}")
    
    # Remove excessive newlines created by URL removal
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Remove lines that only contain URL fragments or are suspiciously long
    lines = cleaned_text.split('\n')
    filtered_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip lines that are just URL fragments or extremely long (likely broken URLs)
        if (len(line) > 200 and 'http' in line) or line.startswith('brw-') or 'ZAxdA-eob4MR40Zy' in line:
            print(f"🧹 [CLEAN-ITINERARY] Removed suspicious line: {line[:100]}...")
            continue
        filtered_lines.append(line)
    
    cleaned_text = '\n'.join(filtered_lines)
    
    print(f"🧹 [CLEAN-ITINERARY] Cleaned itinerary: {len(itinerary_text)} → {len(cleaned_text)} characters")
    return cleaned_text


def process_itinerary_images(itinerary_text: str, flights_info: str, hotels_info: str, sights_info: str) -> str:
    """Process the itinerary to embed actual images instead of just links"""

    # Extract image URLs from the raw data
    image_urls = extract_image_urls_from_data(hotels_info, sights_info)

    # Add images section at the end of the itinerary
    images_section = "\n\n## 📸 Destination Images\n\n"

    if image_urls:
        print(f"🖼️  [ITINERARY-IMAGES] Found {len(image_urls)} valid images to embed")
        for i, (title, url) in enumerate(image_urls.items(), 1):
            # Validate URL before adding
            if url and url.startswith('http') and len(url) > 10:
                images_section += f"### {title}\n"
                images_section += f"![{title}]({url})\n\n"
                print(f"🖼️  [ITINERARY-IMAGES] Added image: {title}")
    else:
        print("🖼️  [ITINERARY-IMAGES] No valid external images found, adding local fallback images")
        # Add some local fallback images to make the itinerary more visually appealing
        fallback_images = [
            ("🏨 Accommodation", "/static/images/fallbacks/hotel.png"),
            ("🍽️ Dining", "/static/images/fallbacks/restaurant.png"),
            ("🏛️ Museums & Culture", "/static/images/fallbacks/museum.png"),
            ("🌳 Parks & Nature", "/static/images/fallbacks/park.png"),
            ("🛍️ Shopping", "/static/images/fallbacks/shopping.png"),
            ("🎭 Entertainment", "/static/images/fallbacks/entertainment.png")
        ]
        
        for title, image_path in fallback_images:
            images_section += f"### {title}\n"
            images_section += f"![{title}]({image_path})\n\n"
            print(f"🖼️  [ITINERARY-IMAGES] Added fallback image: {title}")

    # Insert images section before the practical tips section
    if "## Practical Tips" in itinerary_text:
        itinerary_text = itinerary_text.replace("## Practical Tips", images_section + "## Practical Tips")
    else:
        # If no practical tips section, add images at the end
        itinerary_text += images_section

    return itinerary_text


def extract_image_urls_from_data(hotels_info: str, sights_info: str) -> dict:
    """Extract image URLs from hotels and sights data, filtering out broken URLs"""
    image_urls = {}

    def is_valid_image_url(url: str) -> bool:
        """Check if URL is a valid, accessible image URL"""
        if not url or url == "N/A" or not url.startswith("http"):
            return False
        
        # Filter out known problematic URL patterns
        problematic_patterns = [
            'googleusercontent.com/gps-cs-s/',  # Broken Google User Content URLs
            'lh3.googleusercontent.com/gps-cs-s/',  # Specific broken pattern from the screenshot
            'brw-', # Broken URL fragments
            'ZAxdA-eob4MR40Zy',  # Specific broken URL pattern
            'placeholder.com',  # External placeholder services that may fail
            'via.placeholder'  # External placeholder services that may fail
        ]
        
        for pattern in problematic_patterns:
            if pattern in url:
                print(f"🚫 [EXTRACT-IMAGES] Filtering out problematic URL containing '{pattern}': {url[:100]}...")
                return False
        
        # Check for reasonable URL length (broken URLs tend to be extremely long)
        if len(url) > 500:
            print(f"🚫 [EXTRACT-IMAGES] Filtering out overly long URL: {url[:100]}...")
            return False
            
        return True

    # Extract hotel images
    if "Image:" in hotels_info:
        hotel_lines = hotels_info.split('\n')
        current_hotel = ""
        for line in hotel_lines:
            line = line.strip()
            if line and not line.startswith("Image:") and not line.startswith("Rate:") and not line.startswith("Rating:") and not line.startswith("Location") and not line.startswith("Amenities:") and not line.startswith("Price:"):
                current_hotel = line
            elif line.startswith("Image:") and current_hotel:
                image_url = line.replace("Image:", "").strip()
                if is_valid_image_url(image_url):
                    image_urls[f"🏨 {current_hotel}"] = image_url
                    print(f"🖼️  [EXTRACT-IMAGES] Found valid hotel image: {current_hotel}")

    # Extract sights images
    if "Image:" in sights_info:
        sight_lines = sights_info.split('\n')
        current_sight = ""
        for line in sight_lines:
            line = line.strip()
            if line and not line.startswith("Image:") and not line.startswith("Description:") and not line.startswith("Rating:") and not line.startswith("Price:") and not line.startswith("Here are"):
                current_sight = line
            elif line.startswith("Image:") and current_sight:
                image_url = line.replace("Image:", "").strip()
                if is_valid_image_url(image_url):
                    image_urls[f"📍 {current_sight}"] = image_url
                    print(f"🖼️  [EXTRACT-IMAGES] Found valid sight image: {current_sight}")

    print(f"🖼️  [EXTRACT-IMAGES] Total valid images extracted: {len(image_urls)}")
    return image_urls
