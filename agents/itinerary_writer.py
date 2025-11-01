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
    """Clean up itinerary content by removing Image: lines, broken URLs, and preserving embedded <img> tags"""
    import re
    
    # First, protect all <img> tags (they contain valid URLs)
    img_tags = []
    def save_img(match):
        img_tags.append(match.group(0))
        return f"___IMG_PLACEHOLDER_{len(img_tags)-1}___"
    
    # Save all img tags before cleaning
    protected_text = re.sub(r'<img[^>]*>', save_img, itinerary_text)
    
    # Remove all "Image:" lines with URLs - these should NOT be in the itinerary text
    # Various formats: "Image: url", "* Image: url", "**Image:** url"
    protected_text = re.sub(r'^\s*\*?\*?\s*Image:\s*\*?\*?\s*https?://[^\n]+$', '', protected_text, flags=re.MULTILINE)
    protected_text = re.sub(r'\n\s*\*?\s*Image:\s*https?://[^\s]+', '', protected_text)
    protected_text = re.sub(r'\*\*Image:\*\*\s+https?://[^\s]+', '', protected_text)
    
    # Remove any standalone long URLs that might have escaped (but keep img placeholders)
    protected_text = re.sub(r'(?<!src=")(?<!href=")https?://\S{100,}', '', protected_text)
    
    # Only remove truly broken URL patterns
    broken_url_patterns = [
        r'brw-[A-Za-z0-9_-]{10,}',  # Broken URL fragments (at least 10 chars)
        r'ZAxdA-eob4MR40Zy[A-Za-z0-9_-]*',  # Specific broken pattern
    ]
    
    cleaned_text = protected_text
    for pattern in broken_url_patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text)
        print(f"🧹 [CLEAN-ITINERARY] Removed broken URLs matching pattern: {pattern}")
    
    # Remove excessive newlines created by URL removal
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    
    # Remove lines that are just asterisks or bullets without content
    lines = cleaned_text.split('\n')
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # Keep img placeholders
        if '___IMG_PLACEHOLDER_' in line:
            filtered_lines.append(line)
            continue
        # Skip empty lines with just * or **
        if stripped in ['*', '**', '* *', '* **']:
            continue
        filtered_lines.append(line)
    
    cleaned_text = '\n'.join(filtered_lines)
    
    # Restore all protected img tags
    for i, img_tag in enumerate(img_tags):
        placeholder = f"___IMG_PLACEHOLDER_{i}___"
        cleaned_text = cleaned_text.replace(placeholder, img_tag)
    
    print(f"🧹 [CLEAN-ITINERARY] Cleaned itinerary: {len(itinerary_text)} → {len(cleaned_text)} characters")
    print(f"🖼️  [CLEAN-ITINERARY] Preserved {len(img_tags)} image tags")
    print(f"🧹 [CLEAN-ITINERARY] Removed Image: lines and broken URLs")
    return cleaned_text


def process_itinerary_images(itinerary_text: str, flights_info: str, hotels_info: str, sights_info: str) -> str:
    """Process the itinerary to embed images inline near relevant locations"""

    # Extract image URLs from the raw data
    image_urls = extract_image_urls_from_data(hotels_info, sights_info)

    if not image_urls:
        print("🖼️  [ITINERARY-IMAGES] No valid external images found")
        return itinerary_text

    print(f"🖼️  [ITINERARY-IMAGES] Found {len(image_urls)} valid images to embed inline")
    
    # Try to embed images inline near their corresponding content
    for title, url in image_urls.items():
        # Validate URL before adding
        if url and url.startswith('http') and len(url) > 10:
            # Extract the location/hotel name from the title (remove emoji)
            location_name = title.replace("🏨 ", "").replace("📍 ", "").strip()
            
            # Create a small inline image with error handling
            image_html = f'\n\n<img src="{url}" alt="{location_name}" loading="lazy" onerror="this.style.display=\'none\';" style="max-width: 200px; max-height: 150px; width: auto; height: auto; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin: 12px 0; display: block; object-fit: cover;" />\n\n'
            
            # Look for mentions of this location in the itinerary
            if location_name in itinerary_text:
                # Add image after the first mention
                itinerary_text = itinerary_text.replace(location_name, location_name + image_html, 1)
                print(f"🖼️  [ITINERARY-IMAGES] Embedded inline image for: {location_name}")
            else:
                # Try partial match (first word of location name)
                words = location_name.split()
                if len(words) > 1 and len(words[0]) > 4:
                    first_word = words[0]
                    if first_word in itinerary_text:
                        itinerary_text = itinerary_text.replace(first_word, first_word + image_html, 1)
                        print(f"🖼️  [ITINERARY-IMAGES] Embedded inline image for partial match: {first_word}")

    return itinerary_text


def extract_image_urls_from_data(hotels_info: str, sights_info: str) -> dict:
    """Extract image URLs from hotels and sights data, filtering out broken URLs"""
    image_urls = {}

    def is_valid_image_url(url: str) -> bool:
        """Check if URL is a valid, accessible image URL"""
        if not url or url == "N/A" or not url.startswith("http"):
            return False
        
        # Filter out ONLY truly broken URL patterns (be lenient with Google URLs)
        problematic_patterns = [
            'brw-',  # Broken URL fragments
            'ZAxdA-eob4MR40Zy',  # Specific broken URL pattern
            'placeholder.com',  # External placeholder services
            'via.placeholder'  # External placeholder services
        ]
        
        for pattern in problematic_patterns:
            if pattern in url:
                print(f"🚫 [EXTRACT-IMAGES] Filtering out problematic URL containing '{pattern}': {url[:100]}...")
                return False
        
        # Check for reasonable URL length (broken URLs tend to be extremely long)
        if len(url) > 800:  # Increased from 500 to 800 to allow longer valid URLs
            print(f"🚫 [EXTRACT-IMAGES] Filtering out excessively long URL: {url[:100]}...")
            return False
        
        # Allow Google User Content URLs (they're usually valid, frontend will handle errors)
        if 'googleusercontent.com' in url:
            print(f"✅ [EXTRACT-IMAGES] Allowing Google User Content URL: {url[:80]}...")
            return True
            
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
