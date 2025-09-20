# 🌍 Journezy Trip Planner

<div align="center">

![Journezy Trip Planner](https://img.shields.io/badge/Journezy-Trip%20Planner-orange?style=for-the-badge&logo=airplane)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)
![AI Powered](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-purple?style=for-the-badge&logo=google)

**Your Personal AI-Powered Travel Planning Assistant**

*Plan your dream trips with intelligent recommendations, real-time data, and seamless travel planning*

</div>

---

## ✨ Features

### 🧠 **AI-Powered Intelligence**
- **Gemini AI Integration**: Advanced AI for personalized trip recommendations
- **Multi-Language Support**: 11 languages including English, Hindi, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, and Arabic
- **Smart Itinerary Generation**: Context-aware travel planning based on your preferences
- **Real-time Data**: Live flight and hotel information with pricing

### 🛫 **Comprehensive Travel Planning**
- **Flight Search**: Real-time flight data with pricing and availability
- **Hotel Recommendations**: Curated accommodations with ratings and amenities
- **Places to Visit**: Must-see attractions and hidden gems
- **Detailed Itineraries**: Day-by-day plans with activities and timings
- **Safety Information**: Travel safety advisories for destinations

### 👥 **Smart Traveler Support**
- **Multi-Traveler Planning**: Adults, children, seniors, and toddlers
- **Smart Defaults**: Automatic selection of child-friendly or senior-friendly options
- **Flight Timing Preferences**: 
  - Child-friendly times (10 AM - 6 PM)
  - Senior-friendly times (9 AM - 4 PM)
  - Red-eye and early morning flight avoidance
- **Accessibility Features**: Toddler and senior-friendly accommodations

### 💰 **Budget Management**
- **Multi-Currency Support**: USD and INR with real-time pricing
- **Budget-Aware Planning**: AI considers your budget constraints
- **Transparent Pricing**: Clear cost breakdown

### 🎨 **Modern User Experience**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Beautiful Interface**: Clean, modern UI with smooth animations
- **Enhanced Date Validation**: Future-only date selection with smart adjustments
- **Real-time Form Validation**: Instant feedback and validation
- **PDF Export**: Download complete itineraries

---

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Required API Keys
Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

---

## ⚡ Quick Start

### 1. Clone the Repository

```sh
git clone https://github.com/saitej123/journezy-trip-planner.git
cd journezy-trip-planner
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Set Up Environment

Create a `.env` file with your API keys:

```sh
nano .env
```

Add the required API keys as shown in the prerequisites section.

### 4. Run the Application

```sh
python main.py
```

The application will be available at `http://localhost:8000`

---

## 📖 Usage

### 1. **Access the Application**
- Navigate to `http://localhost:8000`
- Login with credentials: `journezy` / `Journezy2025!`

### 2. **Plan Your Trip**
- **Destinations**: Enter from and to cities
- **Travel Dates**: Select start and end dates (future dates only)
- **Language & Currency**: Choose from 11 languages and 2 currencies
- **Budget**: Enter optional budget amount

### 3. **Traveler Information**
- **Adults**: 1-10 travelers
- **Children**: 0-10 (ages 5-17)
- **Seniors**: 0-10 (ages 65+)
- **Children Under 5**: 0-10 toddlers

### 4. **Special Options**
- **Toddler-Friendly**: Automatically selected when children under 5 are added
- **Senior-Friendly Options**: Automatically selected when seniors are added
- **Safety Check**: Include travel safety information

### 5. **Flight Preferences**
- **Timing Options**:
  - Child-friendly times (10 AM - 6 PM) - ideal for families
  - Senior-friendly times (9 AM - 4 PM) - comfortable scheduling
  - *Note: These options are mutually exclusive*
- **Avoidance Options**:
  - Red-eye flights (10 PM - 6 AM)
  - Early morning flights (before 8 AM)
- **Flight Type**: Direct flights only option

### 6. **Generate & Review**
- Click "Generate Your Perfect Itinerary"
- Review results in organized tabs:
  - **Itinerary**: Complete day-by-day plan
  - **Flights**: Flight options with pricing
  - **Hotels**: Accommodation recommendations
  - **Places**: Attractions and activities

### 7. **Export**
- Download complete itinerary as PDF
- Professional layout for sharing or offline use

---

## 🏗️ Architecture

```
journezy-trip-planner/
├── 📁 agents/                 # AI agents for trip planning
│   ├── deligator.py          # Tour information extraction
│   └── itinerary_writer.py   # Itinerary generation
├── 📁 static/                # Frontend assets
│   ├── css/style.css         # Enhanced UI styling
│   ├── js/main.js           # Smart defaults & validation logic
│   └── images/              # Logo and assets
├── 📁 templates/             # HTML templates
│   └── index.html           # Main application interface
├── 📁 tools/                 # Search integrations
│   ├── flights.py           # Flight search
│   ├── hotels.py            # Hotel search
│   └── places.py            # Places search
├── 📄 main.py               # FastAPI application
├── 📄 workflow.py           # Trip planning workflow
├── 📄 requirements.txt      # Dependencies
└── 📄 README.md            # Documentation
```

### Key Components

#### **Backend**
- **FastAPI**: High-performance web framework
- **Gemini 2.5 Flash**: Advanced AI language model
- **Workflow Engine**: Trip planning orchestration
- **SerpAPI Integration**: Real-time travel data

#### **Frontend**
- **Responsive Design**: Bootstrap 5 with custom CSS
- **Smart Defaults**: Automatic option selection based on travelers
- **Enhanced Date Validation**: Future-only dates with smart adjustments
- **Real-time Validation**: Instant form feedback
- **PDF Generation**: Client-side document creation

---

## 🔧 Configuration

### Environment Variables

```env
# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Optional Authentication (defaults provided)
AUTH_USERNAME=journezy
AUTH_PASSWORD=Journezy2025!
```

### Advanced Settings
- **AI Model**: Gemini 2.5 Flash (latest)
- **Workflow Timeout**: 5 minutes
- **Multi-language**: 11 languages supported
- **Currency Support**: USD and INR

---

## 🚀 API Endpoints

### Main Trip Planning
```http
POST /plan-trip
```

### Additional Endpoints
- `POST /grounded-flights` - Citation-based flight search
- `POST /safety-check` - Travel safety information
- `POST /login` - Authentication
- `GET /app` - Main application interface
- `GET /health` - System health check

---

## 🎯 Recent Updates

### Enhanced User Experience
- **Optimized Logo**: Larger size with minimal padding for better brand visibility
- **Smart Date Selection**: Future-only dates with automatic end date adjustment
- **Flight Timing Clarity**: Specific time ranges for child-friendly (10 AM - 6 PM) and senior-friendly (9 AM - 4 PM) options
- **Improved Validation**: Real-time form validation with user feedback
- **Clean Interface**: Removed test elements for production-ready appearance

### Smart Features
- **Automatic Defaults**: Child and senior-friendly options auto-select based on traveler composition
- **Mutual Exclusion**: Prevents conflicting flight timing preferences
- **Enhanced Accessibility**: Better support for families and seniors
- **Professional Polish**: Streamlined UI with consistent styling

---

<div align="center">

**Made with ❤️ for better travel planning**

[⬆ Back to Top](#-journezy-trip-planner)

</div>