# 🌍 Journezy Trip Planner

<div align="center">

![Journezy Trip Planner](https://img.shields.io/badge/Journezy-Trip%20Planner-orange?style=for-the-badge&logo=airplane)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![AI Powered](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-purple?style=for-the-badge&logo=google)

**Your Personal AI-Powered Travel Planning Assistant**

*Plan your dream trips with intelligent recommendations, real-time data, and seamless booking integration*

🌐 **[Live Demo](https://journezy-trip-planner-217752441008.asia-south1.run.app/)** | 
[🚀 Features](#-features) • [📋 Prerequisites](#-prerequisites) • [⚡ Quick Start](#-quick-start) • [🔧 Configuration](#-configuration) • [📖 Usage](#-usage) 
</div>

---

## ✨ Features

### 🧠 **AI-Powered Intelligence**
- **Gemini models Integration**: Advanced AI for personalized trip recommendations with grounded data retrieval
- **Multi-Language Support**: 11 languages including English, Hindi, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, and Arabic
- **Smart Itinerary Generation**: Context-aware travel planning based on your preferences
- **Grounded Flight Search**: Advanced flight search with citation-based recommendations

### 🛫 **Comprehensive Travel Planning**
- **Real-time Flight Search**: Live flight data with pricing and availability
- **Hotel Recommendations**: Curated accommodation options with ratings, amenities, and location scores
- **Places to Visit**: Must-see attractions and hidden gems with detailed descriptions
- **Detailed Itineraries**: Day-by-day plans with activities, timings, and recommendations
- **Safety Checks**: Travel safety information and advisories for destinations

### 👥 **Advanced Traveler Support**
- **Multi-Traveler Planning**: Support for adults, children, seniors, and children under 5
- **Accessibility Features**: Senior-friendly and toddler-friendly options
- **Flight Preferences**: Customizable options for red-eye flights, early morning departures, and direct flights
- **Special Considerations**: Child-friendly and senior-friendly activity recommendations

### 💰 **Budget Management**
- **Multi-Currency Support**: USD and INR with real-time pricing
- **Budget-Aware Planning**: AI considers your budget constraints across all recommendations
- **Cost Optimization**: Smart recommendations within your price range
- **Transparent Pricing**: Clear price breakdown for flights, hotels, and activities

### 🎨 **Modern User Experience**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Beautiful UI**: Clean, modern interface with smooth animations and AOS effects
- **Real-time Updates**: Live data and instant recommendations
- **Interactive Elements**: Tabbed interface for flights, hotels, places, and itinerary
- **Form Validation**: Real-time input validation with user feedback

### 📱 **Booking Integration**
- **EaseMyTrip Integration**: Direct booking links for flights and hotels
- **Pre-filled Search**: Automatic form population with your travel details
- **External Links**: Seamless redirection to booking platforms with search parameters

### 📄 **Document Generation & Export**
- **PDF Download**: Generate and download complete itineraries as PDF documents
- **Markdown Support**: Flexible document formatting with markdown parsing
- **Print-Ready**: Professional layouts for offline reference
- **Client-side PDF Generation**: Fast PDF creation using jsPDF library

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** 
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Add your API keys here
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_key
```

---

## ⚡ Quick Start

### 1. Clone the Repository

```sh
git clone https://github.com/your-username/journezy-trip-planner.git
cd journezy-trip-planner
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Set Up Environment

```sh
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

### 4. Run the Application

```sh
python main.py
```

### Server Configuration
The application runs on `http://localhost:8000` by default. To change the port or host:

```python
# In main.py, modify the uvicorn.run() call
uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 📖 Usage

### 1. **Login**
- Navigate to the application URL
- Enter your credentials (default: `journezy` / `Journezy2025!`)
- Click "Login" to access the trip planner

### 2. **Plan Your Trip**
- **From City**: Enter your departure city
- **To City**: Enter your destination city
- **Travel Dates**: Select start and end dates
- **Language**: Choose your preferred language (11 languages supported)
- **Currency**: Select USD or INR
- **Budget**: Enter your total trip budget (optional)

#### 2.1. **Traveler Information**
- **Adults**: Number of adult travelers (1-10)
- **Children**: Number of children (0-10)
- **Seniors**: Number of senior citizens 65+ (0-10)
- **Children Under 5**: Number of toddlers (0-10)

#### 2.2. **Special Options**
- **Toddler-Friendly**: Include toddler-friendly activities and accommodations
- **Senior-Friendly**: Include senior citizen-friendly options
- **Safety Check**: Include travel safety information and advisories

#### 2.3. **Flight Preferences**
- **Avoid Red-Eye Flights**: Skip flights departing 10 PM - 6 AM
- **Avoid Early Morning**: Skip flights before 8 AM
- **Child-Friendly Times**: Prefer mid-day flights (10 AM - 6 PM)
- **Senior-Friendly Times**: Prefer comfortable flight times
- **Direct Flights Only**: Prefer non-stop flights

- **Additional Instructions**: Add any specific requirements

### 3. **Generate Itinerary**
- Click "Generate Your Perfect Itinerary"
- Wait for AI processing (usually 30-60 seconds with 5-minute timeout)
- Review the generated recommendations with real-time data

### 4. **Explore Results**
- **Itinerary Tab**: See your complete day-by-day plan with markdown formatting
- **Flights Tab**: View flight options with pricing, timing, and direct booking links
- **Hotels Tab**: Browse accommodation recommendations with ratings and amenities
- **Places Tab**: Discover attractions and activities with descriptions and ratings

### 5. **Book Your Trip**
- Click "Book on EaseMyTrip" for flights and hotels
- Links open in new tabs with pre-filled search parameters based on your trip details
- Complete your bookings on the external platform

### 6. **Download Itinerary**
- Click "Download PDF" to generate and save your complete itinerary
- Professional PDF layout with trip details and generated content
- Share with travel companions or keep for offline reference

---


## 🏗️ Architecture

```
journezy-trip-planner/
├── 📁 agents/                 # AI agents for different tasks
│   ├── deligator.py          # Tour information extraction and delegation
│   └── itinerary_writer.py   # AI-powered itinerary generation
├── 📁 static/                # Frontend assets
│   ├── css/style.css         # Comprehensive styling and themes
│   ├── js/main.js           # Frontend logic with AOS animations
│   ├── images/              # Logo and visual assets
│   └── login.html           # Authentication page
├── 📁 templates/             # HTML templates
│   └── index.html           # Main application interface
├── 📁 tools/                 # Utility tools and services
│   ├── flights.py           # Flight search integration
│   ├── hotels.py            # Hotel search integration
│   └── places.py            # Places and attractions search
├── 📄 main.py               # FastAPI application with comprehensive APIs
├── 📄 workflow.py           # Main workflow orchestration with timeout handling
├── 📄 grounding_service.py  # Grounded data retrieval and citation services
├── 📄 run.py                # Application runner
├── 📄 requirements.txt      # Python dependencies
├── 📄 Dockerfile           # Container configuration
├── 📄 LICENSE              # MIT license
└── 📄 README.md            # Comprehensive documentation
```

### 🔧 **Key Components**

#### **Backend Architecture**
- **FastAPI Application**: High-performance async web framework
- **Gemini 2.5 Flash Integration**: Advanced AI language model
- **Workflow Engine**: Orchestrates trip planning pipeline
- **Grounding Service**: Citation-based data retrieval
- **Tool Integration**: SerpAPI for real-time travel data

#### **Frontend Architecture**
- **Responsive Design**: Bootstrap 5 with custom CSS
- **Interactive UI**: AOS animations and smooth transitions
- **Real-time Validation**: Client-side form validation
- **PDF Generation**: Client-side PDF creation with jsPDF
- **Tab Navigation**: Organized content presentation

#### **API Endpoints**
- `POST /plan-trip`: Comprehensive trip planning with all features
- `POST /grounded-flights`: Citation-based flight recommendations
- `POST /safety-check`: Travel safety information
- `POST /login`: Authentication endpoint
- `GET /app`: Main application interface

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Optional Authentication (defaults provided)
AUTH_USERNAME=journezy
AUTH_PASSWORD=Journezy2025!
```

### Advanced Configuration

#### **Gemini AI Settings**
- Model: `gemini-2.5-flash` (latest version)
- Temperature: Optimized for travel recommendations
- Safety settings: Configured for travel content

#### **SerpAPI Integration**
- Real-time flight data
- Hotel information with ratings
- Places and attractions data
- Currency-specific pricing

#### **Timeout Settings**
- Workflow timeout: 5 minutes
- Individual API calls: 30 seconds
- Frontend request timeout: 5 minutes

---

## 🚀 API Reference

### Main Trip Planning Endpoint

```http
POST /plan-trip
```

**Request Body:**

```json
{
  "from_city": "New York",
  "to_city": "Paris",
  "start_date": "2025-06-01",
  "end_date": "2025-06-07",
  "language": "en",
  "currency": "USD",
  "budget_amount": 3000,
  "travelers": {
    "adults": 2,
    "children": 1,
    "seniors": 0,
    "children_under_5": 0
  },
  "flight_preferences": {
    "avoid_red_eye": true,
    "avoid_early_morning": false,
    "child_friendly": true,
    "senior_friendly": false,
    "direct_flights_only": false
  },
  "consider_toddler_friendly": false,
  "consider_senior_friendly": false,
  "safety_check": true,
  "additional_instructions": "Budget-friendly options preferred"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Trip planned successfully",
  "itinerary": {
    "flights": {
      "data": "formatted flight information",
      "formatted": true
    },
    "hotels": {
      "data": "formatted hotel information", 
      "formatted": true
    },
    "places": {
      "data": "formatted places information",
      "formatted": true
    },
    "itinerary": {
      "data": "complete markdown itinerary",
      "formatted": true
    }
  },
  "document": "base64_encoded_pdf_or_markdown",
  "document_type": "pdf|markdown"
}
```

### Other Endpoints

#### Safety Check

```http
POST /safety-check
```

#### Grounded Flights

```http
POST /grounded-flights
```

#### Authentication

```http
POST /login
```

---

## 🐳 Docker Deployment

```sh
# Build the image
docker build -t journezy-trip-planner .

# Run the container
docker run -p 8000:8000 --env-file .env journezy-trip-planner
```

---

## 🧪 Testing

Run the application locally:

```sh
python run.py
```

The application will be available at `http://localhost:8000`

---

<div align="center">

**Made by the WNS Journezy Team**

[⬆ Back to Top](#-journezy-trip-planner)

</div>