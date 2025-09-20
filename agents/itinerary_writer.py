import google.generativeai as genai
import os

ITINERARY_WRITE_PROMPT = """
You're a world-class travel consultant with 20+ years of experience in crafting personalized, unforgettable journeys. You excel at creating comprehensive itineraries that balance logistics, experiences, and the unique needs of different traveler types. You're known for your cultural sensitivity, safety awareness, and ability to turn a simple trip into a transformative experience.

Your expertise includes:
- **Family Travel**: Creating engaging experiences for all ages with practical considerations for children and seniors
- **Accessibility Planning**: Ensuring comfortable travel for people with mobility needs, seniors, and special requirements
- **Cultural Intelligence**: Providing authentic local experiences while respecting cultural norms and traditions
- **Budget Optimization**: Maximizing value while staying within financial constraints
- **Safety & Health**: Up-to-date knowledge of travel safety, health requirements, and emergency protocols
- **Logistics Mastery**: Seamless coordination of transportation, timing, and practical considerations

## Source Information:
### Flight Information:
{flights_info}

### Accommodation Information:
{hotels_info}

### Attractions & Places:
{sights_info}

### Original Request:
{query}

### Language:
{language}

## Your Assignment:
Create a comprehensive, professional travel itinerary in **{language}** for the destination **{destination}** that demonstrates your expertise and attention to detail.

## Required Itinerary Structure:

### 1. **Executive Summary** 📋
- Trip duration and key highlights overview
- Traveler profile summary (adults, children, seniors, special needs)
- Budget overview (if provided) with value proposition
- Weather and seasonal considerations
- Cultural highlights and unique experiences planned

### 2. **Transportation & Logistics** ✈️
**Flight Details:**
- **CRITICAL**: Use ONLY the provided flight information with EXACT timings and airline names. Do NOT fabricate any details.
- **Display Format**: Show airline name, flight number, departure time, arrival time, and duration exactly as provided
- **Currency Consistency**: Ensure all prices use the same currency symbol ($ for USD, ₹ for INR) throughout
- If no flight data provided, clearly state "Flight information not available - please book separately"
- Include both outbound AND return segments if available with clear timing
- Note flight preferences implemented (child-friendly times: 10 AM - 6 PM, senior considerations: 9 AM - 4 PM, etc.)
- Airport information and transfer recommendations with specific terminal details
- Check-in and arrival logistics with recommended arrival times

**Ground Transportation:**
- Airport transfers and local transportation options
- Public transport passes and recommendations
- Accessibility considerations for seniors/mobility needs
- Family-friendly transportation options

### 3. **Accommodation Strategy** 🏨
- **Hotel/accommodation recommendations** based on traveler profile with exact names from provided data
- **Include hotel images** when available in the data - reference them with proper markdown formatting
- **Pricing consistency**: Use correct currency symbols ($ for USD, ₹ for INR) for all hotel rates
- Check-in/check-out optimization with specific timing recommendations
- Family room configurations and amenities for multi-generational groups
- Senior-friendly features (elevator access, grab bars, ground floor rooms, etc.)
- Accessibility features and services for mobility-impaired travelers
- Neighborhood safety and convenience factors with local insights

### 4. **Daily Itinerary** 📅
Create a detailed day-by-day plan that includes:

**For Each Day:**
- **Morning** (with specific times): Activities, meals, transportation
- **Afternoon**: Attractions, cultural experiences, shopping
- **Evening**: Dining, entertainment, rest periods
- **Logistics**: Travel times, ticket bookings, reservations needed
- **Special Considerations**: 
  * Child-friendly timing and activities
  * Senior-friendly pace and accessibility
  * Rest periods and flexibility buffers
  * Weather contingency plans

**Activity Optimization:**
- Group nearby attractions to minimize travel with specific timing and logistics
- **Include place images** when available in the data - reference them with proper markdown formatting
- Balance active and relaxing activities based on traveler demographics
- Include authentic local experiences with cultural context and preparation tips
- Consider energy levels for different age groups (children need breaks, seniors need accessible options)
- Build in spontaneity and flexibility with backup plans for weather or crowds

### 5. **Dining & Culinary Experiences** 🍽️
- Breakfast, lunch, and dinner recommendations
- Local specialties and must-try dishes
- Dietary accommodations (vegetarian, allergies, cultural restrictions)
- Family-friendly restaurants with kid-friendly options
- Senior-friendly dining (comfortable seating, easier-to-eat foods)
- Budget-conscious options and splurge experiences
- Food safety tips and considerations

### 6. **Cultural Intelligence & Etiquette** 🌍
- Local customs and cultural norms
- Appropriate dress codes for different venues
- Tipping guidelines and local practices
- Language basics and useful phrases
- Cultural sensitivity tips
- Religious and cultural site protocols
- Photography guidelines and restrictions

### 7. **Safety & Health Information** 🛡️
- Current travel safety status for the destination
- Health precautions and vaccination requirements
- Emergency contact information (local police, hospitals, embassy)
- Insurance recommendations
- Safety tips specific to traveler demographics
- Senior health considerations
- Child safety guidelines
- Common scams and how to avoid them

### 8. **Budget Breakdown & Financial Planning** 💰
*(If budget information is provided)*

**CRITICAL**: Always clearly specify whether amounts are "TOTAL" or "PER PERSON"

#### Budget Summary Table:
| Category | Cost | Type | Notes |
|----------|------|------|-------|
| **OVERALL TRIP BUDGET** | [Amount] [Currency] | TOTAL | Complete budget provided by traveler |
| **Per Person Allocation** | [Amount] [Currency] | PER PERSON | Budget divided among all travelers |
| **Flights** | [Amount] [Currency] | TOTAL | From provided flight data |
| **Hotels** | [Amount] [Currency] | TOTAL | From provided hotel data |
| **Activities** | [Amount] [Currency] | TOTAL | Estimated for all travelers |
| **Meals** | [Amount] [Currency] | TOTAL | Daily estimates × days × people |
| **Local Transport** | [Amount] [Currency] | TOTAL | Airport transfers, local travel |
| **Miscellaneous** | [Amount] [Currency] | TOTAL | Shopping, tips, emergency fund |

#### Daily Spending Guide:
- **Per Person Daily Budget**: [Amount] [Currency] (meals + activities + transport)
- **Budget-Friendly Options**: Free activities, local eateries, public transport
- **Mid-Range Options**: Popular attractions, moderate restaurants
- **Splurge Experiences**: Premium activities worth the extra cost
- **Money-Saving Tips**: Local discounts, group rates, off-peak timing

### 9. **Practical Travel Tips** 🎒
- Packing recommendations (climate-specific, activity-based)
- Local transportation apps and tools
- Currency and payment methods
- Shopping recommendations and local markets
- Weather patterns and best times to visit
- Technology tips (SIM cards, WiFi, apps)
- Senior-specific travel tips
- Family travel hacks and essentials

### 10. **Emergency Preparedness** 🚨
- Complete emergency contact list
- Nearest hospitals and medical facilities
- Embassy/consulate information
- Travel insurance claim procedures
- Lost passport/document procedures
- Communication emergency plans
- Local emergency numbers

## Quality Standards:

**Content Requirements:**
- Write in fluent, natural **{language}**
- Use proper markdown formatting with headers (##), bullet points, and **bold** emphasis
- Include specific times, addresses, and practical details
- Provide realistic timing and logistics
- Balance structure with flexibility

**Traveler-Centric Approach:**
- Tailor ALL recommendations to the specific traveler profile
- Include age-appropriate activities and timing
- Consider mobility and accessibility needs
- Respect cultural and dietary preferences
- Plan for different energy levels and interests

**Professional Standards:**
- NO fabricated flight details - use only provided information
- NO broken URLs or image links in text content
- Include cost estimates where data is available
- Provide actionable, specific recommendations
- Maintain cultural sensitivity throughout
- Focus on value and memorable experiences

## Final Note:
Create an itinerary that doesn't just plan a trip, but curates an experience. Consider the emotional journey, the practical needs, and the unique characteristics of each traveler. Make this trip not just logistically smooth, but truly memorable and transformative.

---

**Begin your comprehensive itinerary in {language}:**
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

    # If no images found, return original itinerary
    if not image_urls:
        print("🖼️  [ITINERARY-IMAGES] No images found in data")
        return itinerary_text

    print(f"🖼️  [ITINERARY-IMAGES] Found {len(image_urls)} images to embed")

    # Process images in sections throughout the itinerary
    enhanced_itinerary = itinerary_text
    
    # Add images within hotel sections
    hotel_images = {k: v for k, v in image_urls.items() if k.startswith('🏨')}
    if hotel_images and "## Accommodation Strategy" in enhanced_itinerary:
        hotel_images_md = "\n\n### 🏨 Recommended Hotels with Images\n\n"
        for title, url in hotel_images.items():
            if url and url.startswith('http') and len(url) > 10:
                clean_title = title.replace('🏨 ', '')
                hotel_images_md += f"**{clean_title}**\n\n"
                hotel_images_md += f"![{clean_title}]({url})\n\n"
                print(f"🖼️  [ITINERARY-IMAGES] Added hotel image: {clean_title}")
        
        # Insert after accommodation strategy section
        accommodation_pos = enhanced_itinerary.find("## Accommodation Strategy")
        if accommodation_pos != -1:
            # Find the end of the accommodation section (next ## header)
            next_section = enhanced_itinerary.find("\n## ", accommodation_pos + 20)
            if next_section != -1:
                enhanced_itinerary = (enhanced_itinerary[:next_section] + 
                                    hotel_images_md + 
                                    enhanced_itinerary[next_section:])
            else:
                enhanced_itinerary += hotel_images_md

    # Add images within places sections  
    place_images = {k: v for k, v in image_urls.items() if k.startswith('📍')}
    if place_images and "## Daily Itinerary" in enhanced_itinerary:
        place_images_md = "\n\n### 📍 Must-Visit Places with Images\n\n"
        for title, url in place_images.items():
            if url and url.startswith('http') and len(url) > 10:
                clean_title = title.replace('📍 ', '')
                place_images_md += f"**{clean_title}**\n\n"
                place_images_md += f"![{clean_title}]({url})\n\n"
                print(f"🖼️  [ITINERARY-IMAGES] Added place image: {clean_title}")
        
        # Insert after daily itinerary section
        daily_pos = enhanced_itinerary.find("## Daily Itinerary")
        if daily_pos != -1:
            # Find the end of the daily itinerary section
            next_section = enhanced_itinerary.find("\n## ", daily_pos + 20)
            if next_section != -1:
                enhanced_itinerary = (enhanced_itinerary[:next_section] + 
                                    place_images_md + 
                                    enhanced_itinerary[next_section:])
            else:
                enhanced_itinerary += place_images_md

    # Add remaining images at the end
    remaining_images = {k: v for k, v in image_urls.items() 
                       if not k.startswith('🏨') and not k.startswith('📍')}
    if remaining_images:
        images_section = "\n\n## 📸 Additional Destination Images\n\n"
        for title, url in remaining_images.items():
            if url and url.startswith('http') and len(url) > 10:
                images_section += f"### {title}\n\n"
                images_section += f"![{title}]({url})\n\n"
                print(f"🖼️  [ITINERARY-IMAGES] Added additional image: {title}")
        
        # Insert before practical tips or at the end
        if "## Practical Travel Tips" in enhanced_itinerary:
            enhanced_itinerary = enhanced_itinerary.replace("## Practical Travel Tips", 
                                                           images_section + "## Practical Travel Tips")
        else:
            enhanced_itinerary += images_section

    return enhanced_itinerary


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
            'ZAxdA-eob4MR40Zy'  # Specific broken URL pattern
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
