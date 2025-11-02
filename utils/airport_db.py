"""
Airport Database Utility
Manages airport codes, names, and locations in SQLite database
Downloads comprehensive airport data from public sources
"""
import sqlite3
import os
from typing import List, Dict, Optional
import csv
import urllib.request
import io

DB_PATH = "airports.db"


def init_database():
    """Initialize the airport database if it doesn't exist"""
    if os.path.exists(DB_PATH):
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create airports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            city TEXT,
            country TEXT,
            country_code TEXT,
            latitude REAL,
            longitude REAL,
            timezone TEXT
        )
    """)
    
    # Create index on code for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_code ON airports(code)
    """)
    
    # Create index on name for search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_name ON airports(name)
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ [AIRPORT-DB] Database initialized at {DB_PATH}")


def download_airports_data():
    """Download comprehensive airport data from OurAirports (public database)"""
    print("📥 [AIRPORT-DB] Downloading airport data from OurAirports...")
    
    try:
        # OurAirports provides comprehensive airport data
        # URL: https://ourairports.com/data/airports.csv
        url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
        
        print(f"🌐 [AIRPORT-DB] Fetching data from {url}...")
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')
        
        print(f"✅ [AIRPORT-DB] Downloaded {len(data)} bytes of airport data")
        return data, "ourairports"
    
    except Exception as e:
        print(f"⚠️ [AIRPORT-DB] Failed to download from OurAirports: {e}")
        print("📥 [AIRPORT-DB] Trying alternative source: OpenFlights...")
        
        try:
            # Alternative: OpenFlights airport database
            url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
            
            print("🌐 [AIRPORT-DB] Fetching data from OpenFlights...")
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read().decode('utf-8')
            
            print("✅ [AIRPORT-DB] Downloaded OpenFlights data")
            return data, "openflights"
        
        except Exception as e2:
            print(f"❌ [AIRPORT-DB] Failed to download from both sources: {e2}")
            return None, None


def parse_ourairports_csv(csv_data: str):
    """Parse OurAirports CSV format"""
    airports = []
    reader = csv.DictReader(io.StringIO(csv_data))
    
    country_code_map = {
        # Common country code mappings
        'United States': 'US', 'United Kingdom': 'GB', 'Canada': 'CA',
        'Australia': 'AU', 'New Zealand': 'NZ', 'India': 'IN',
        'China': 'CN', 'Japan': 'JP', 'South Korea': 'KR',
        'Germany': 'DE', 'France': 'FR', 'Italy': 'IT', 'Spain': 'ES',
        'Netherlands': 'NL', 'Belgium': 'BE', 'Switzerland': 'CH',
        'Brazil': 'BR', 'Mexico': 'MX', 'Argentina': 'AR',
    }
    
    timezone_map = {
        # Common timezone mappings
        'US': 'America/New_York', 'CA': 'America/Toronto',
        'GB': 'Europe/London', 'FR': 'Europe/Paris', 'DE': 'Europe/Berlin',
        'IT': 'Europe/Rome', 'ES': 'Europe/Madrid', 'NL': 'Europe/Amsterdam',
        'AU': 'Australia/Sydney', 'NZ': 'Pacific/Auckland',
        'IN': 'Asia/Kolkata', 'CN': 'Asia/Shanghai', 'JP': 'Asia/Tokyo',
        'KR': 'Asia/Seoul', 'BR': 'America/Sao_Paulo', 'MX': 'America/Mexico_City',
    }
    
    for row in reader:
        iata_code = row.get('iata_code', '').strip().upper()
        # Only include airports with IATA codes (3-letter codes)
        if not iata_code or len(iata_code) != 3:
            continue
        
        name = row.get('name', '').strip()
        city = row.get('municipality', '').strip()
        country = row.get('iso_country', '').strip()
        
        # Get country code
        country_code = country if len(country) == 2 else country_code_map.get(country, '')
        
        # Parse coordinates
        try:
            latitude = float(row.get('latitude_deg', 0)) if row.get('latitude_deg') else None
            longitude = float(row.get('longitude_deg', 0)) if row.get('longitude_deg') else None
        except (ValueError, TypeError):
            latitude = longitude = None
        
        # Get timezone
        timezone = row.get('timezone', '') or timezone_map.get(country_code, '')
        
        airports.append((
            iata_code,
            name,
            city,
            country,
            country_code,
            latitude,
            longitude,
            timezone
        ))
    
    return airports


def parse_openflights_csv(csv_data: str):
    """Parse OpenFlights CSV format"""
    airports = []
    reader = csv.reader(io.StringIO(csv_data))
    
    country_code_map = {
        'United States': 'US', 'United Kingdom': 'GB', 'Canada': 'CA',
        'Australia': 'AU', 'New Zealand': 'NZ', 'India': 'IN',
        'China': 'CN', 'Japan': 'JP', 'South Korea': 'KR',
        'Germany': 'DE', 'France': 'FR', 'Italy': 'IT', 'Spain': 'ES',
    }
    
    timezone_map = {
        'US': 'America/New_York', 'CA': 'America/Toronto',
        'GB': 'Europe/London', 'FR': 'Europe/Paris', 'DE': 'Europe/Berlin',
        'IT': 'Europe/Rome', 'ES': 'Europe/Madrid', 'NL': 'Europe/Amsterdam',
        'AU': 'Australia/Sydney', 'NZ': 'Pacific/Auckland',
        'IN': 'Asia/Kolkata', 'CN': 'Asia/Shanghai', 'JP': 'Asia/Tokyo',
        'KR': 'Asia/Seoul', 'BR': 'America/Sao_Paulo', 'MX': 'America/Mexico_City',
    }
    
    for row in reader:
        if len(row) < 14:
            continue
        
        # OpenFlights format: id, name, city, country, iata, icao, lat, lon, alt, timezone, dst, tz, type, source
        iata_code = row[4].strip().upper() if len(row) > 4 else ''
        # Only include airports with IATA codes
        if not iata_code or len(iata_code) != 3 or iata_code == '\\N':
            continue
        
        name = row[1].strip() if len(row) > 1 else ''
        city = row[2].strip() if len(row) > 2 else ''
        country = row[3].strip() if len(row) > 3 else ''
        country_code = country if len(country) == 2 else country_code_map.get(country, '')
        
        try:
            latitude = float(row[6]) if len(row) > 6 and row[6] else None
            longitude = float(row[7]) if len(row) > 7 and row[7] else None
        except (ValueError, TypeError):
            latitude = longitude = None
        
        timezone = (row[9] if len(row) > 9 else '') or timezone_map.get(country_code, '')
        
        airports.append((
            iata_code,
            name,
            city,
            country,
            country_code,
            latitude,
            longitude,
            timezone
        ))
    
    return airports


def get_popular_international_airports():
    """Get list of popular international tourist destination airports worldwide"""
    return [
        # === UNITED STATES ===
        ("JFK", "John F. Kennedy International Airport", "New York", "United States", "US", 40.6413, -73.7781, "America/New_York"),
        ("EWR", "Newark Liberty International Airport", "Newark", "United States", "US", 40.6925, -74.1687, "America/New_York"),
        ("LAX", "Los Angeles International Airport", "Los Angeles", "United States", "US", 33.9425, -118.4081, "America/Los_Angeles"),
        ("MIA", "Miami International Airport", "Miami", "United States", "US", 25.7959, -80.2870, "America/New_York"),
        ("LAS", "McCarran International Airport", "Las Vegas", "United States", "US", 36.0840, -115.1537, "America/Los_Angeles"),
        ("SFO", "San Francisco International Airport", "San Francisco", "United States", "US", 37.6213, -122.3790, "America/Los_Angeles"),
        ("HNL", "Daniel K. Inouye International Airport", "Honolulu", "United States", "US", 21.3206, -157.9242, "Pacific/Honolulu"),
        ("ORD", "O'Hare International Airport", "Chicago", "United States", "US", 41.9786, -87.9048, "America/Chicago"),
        ("DFW", "Dallas/Fort Worth International Airport", "Dallas", "United States", "US", 32.8998, -97.0403, "America/Chicago"),
        ("IAH", "George Bush Intercontinental Airport", "Houston", "United States", "US", 29.9844, -95.3414, "America/Chicago"),
        ("ATL", "Hartsfield-Jackson Atlanta International Airport", "Atlanta", "United States", "US", 33.6367, -84.4281, "America/New_York"),
        ("SEA", "Seattle-Tacoma International Airport", "Seattle", "United States", "US", 47.4502, -122.3088, "America/Los_Angeles"),
        ("BOS", "Logan International Airport", "Boston", "United States", "US", 42.3656, -71.0096, "America/New_York"),
        ("IAD", "Washington Dulles International Airport", "Washington DC", "United States", "US", 38.9445, -77.4558, "America/New_York"),
        ("PHX", "Phoenix Sky Harbor International Airport", "Phoenix", "United States", "US", 33.4342, -112.0116, "America/Phoenix"),
        ("DEN", "Denver International Airport", "Denver", "United States", "US", 39.8617, -104.6731, "America/Denver"),
        ("PDX", "Portland International Airport", "Portland", "United States", "US", 45.5898, -122.5951, "America/Los_Angeles"),
        ("SAN", "San Diego International Airport", "San Diego", "United States", "US", 32.7338, -117.1933, "America/Los_Angeles"),
        
        # === UNITED KINGDOM ===
        ("LHR", "London Heathrow Airport", "London", "United Kingdom", "GB", 51.4700, -0.4543, "Europe/London"),
        ("LGW", "London Gatwick Airport", "London", "United Kingdom", "GB", 51.1537, -0.1821, "Europe/London"),
        ("EDI", "Edinburgh Airport", "Edinburgh", "United Kingdom", "GB", 55.9500, -3.3725, "Europe/London"),
        ("MAN", "Manchester Airport", "Manchester", "United Kingdom", "GB", 53.3537, -2.2750, "Europe/London"),
        
        # === FRANCE ===
        ("CDG", "Charles de Gaulle Airport", "Paris", "France", "FR", 49.0097, 2.5479, "Europe/Paris"),
        ("NCE", "Nice Côte d'Azur Airport", "Nice", "France", "FR", 43.6584, 7.2159, "Europe/Paris"),
        ("LYS", "Lyon-Saint Exupéry Airport", "Lyon", "France", "FR", 45.7264, 5.0908, "Europe/Paris"),
        ("MRS", "Marseille Provence Airport", "Marseille", "France", "FR", 43.4393, 5.2214, "Europe/Paris"),
        ("BOD", "Bordeaux-Mérignac Airport", "Bordeaux", "France", "FR", 44.8283, -0.7156, "Europe/Paris"),
        ("TLS", "Toulouse-Blagnac Airport", "Toulouse", "France", "FR", 43.6291, 1.3638, "Europe/Paris"),
        
        # === ITALY ===
        ("FCO", "Leonardo da Vinci-Fiumicino Airport", "Rome", "Italy", "IT", 41.8003, 12.2389, "Europe/Rome"),
        ("MXP", "Milan Malpensa Airport", "Milan", "Italy", "IT", 45.6306, 8.7281, "Europe/Rome"),
        ("VCE", "Venice Marco Polo Airport", "Venice", "Italy", "IT", 45.5053, 12.3519, "Europe/Rome"),
        ("FLR", "Florence Airport", "Florence", "Italy", "IT", 43.8100, 11.2051, "Europe/Rome"),
        ("NAP", "Naples International Airport", "Naples", "Italy", "IT", 40.8860, 14.2908, "Europe/Rome"),
        ("BGY", "Milan Bergamo Airport", "Bergamo", "Italy", "IT", 45.6739, 9.7042, "Europe/Rome"),
        
        # === SPAIN ===
        ("MAD", "Madrid-Barajas Airport", "Madrid", "Spain", "ES", 40.4839, -3.5680, "Europe/Madrid"),
        ("BCN", "Barcelona-El Prat Airport", "Barcelona", "Spain", "ES", 41.2971, 2.0785, "Europe/Madrid"),
        ("AGP", "Málaga-Costa del Sol Airport", "Málaga", "Spain", "ES", 36.6750, -4.4992, "Europe/Madrid"),
        ("PMI", "Palma de Mallorca Airport", "Palma", "Spain", "ES", 39.5536, 2.7388, "Europe/Madrid"),
        ("LPA", "Gran Canaria Airport", "Las Palmas", "Spain", "ES", 27.9319, -15.3866, "Atlantic/Canary"),
        ("TFN", "Tenerife Norte Airport", "Tenerife", "Spain", "ES", 28.4827, -16.3415, "Atlantic/Canary"),
        
        # === GERMANY ===
        ("FRA", "Frankfurt am Main Airport", "Frankfurt", "Germany", "DE", 50.0379, 8.5622, "Europe/Berlin"),
        ("MUC", "Munich Airport", "Munich", "Germany", "DE", 48.3538, 11.7861, "Europe/Berlin"),
        ("BER", "Berlin Brandenburg Airport", "Berlin", "Germany", "DE", 52.3667, 13.5033, "Europe/Berlin"),
        ("HAM", "Hamburg Airport", "Hamburg", "Germany", "DE", 53.6304, 9.9882, "Europe/Berlin"),
        ("DUS", "Düsseldorf Airport", "Düsseldorf", "Germany", "DE", 51.2895, 6.7668, "Europe/Berlin"),
        ("CGN", "Cologne Bonn Airport", "Cologne", "Germany", "DE", 50.8659, 7.1427, "Europe/Berlin"),
        
        # === NETHERLANDS ===
        ("AMS", "Amsterdam Airport Schiphol", "Amsterdam", "Netherlands", "NL", 52.3105, 4.7683, "Europe/Amsterdam"),
        
        # === BELGIUM ===
        ("BRU", "Brussels Airport", "Brussels", "Belgium", "BE", 50.9014, 4.4844, "Europe/Brussels"),
        
        # === LUXEMBOURG ===
        ("LUX", "Luxembourg Airport", "Luxembourg", "Luxembourg", "LU", 49.6233, 6.2044, "Europe/Luxembourg"),
        
        # === GREECE ===
        ("ATH", "Athens International Airport", "Athens", "Greece", "GR", 37.9364, 23.9445, "Europe/Athens"),
        ("JMK", "Mykonos Airport", "Mykonos", "Greece", "GR", 37.4351, 25.3481, "Europe/Athens"),
        ("JTR", "Santorini (Thira) National Airport", "Santorini", "Greece", "GR", 36.3992, 25.4792, "Europe/Athens"),
        
        # === PORTUGAL ===
        ("LIS", "Lisbon Portela Airport", "Lisbon", "Portugal", "PT", 38.7813, -9.1359, "Europe/Lisbon"),
        ("OPO", "Francisco Sá Carneiro Airport", "Porto", "Portugal", "PT", 41.2481, -8.6814, "Europe/Lisbon"),
        
        # === SWITZERLAND ===
        ("ZUR", "Zurich Airport", "Zurich", "Switzerland", "CH", 47.4647, 8.5492, "Europe/Zurich"),
        ("GVA", "Geneva Airport", "Geneva", "Switzerland", "CH", 46.2380, 6.1090, "Europe/Zurich"),
        
        # === AUSTRIA ===
        ("VIE", "Vienna International Airport", "Vienna", "Austria", "AT", 48.1103, 16.5697, "Europe/Vienna"),
        
        # === TURKEY ===
        ("IST", "Istanbul Airport", "Istanbul", "Turkey", "TR", 41.2622, 28.7278, "Europe/Istanbul"),
        ("ANK", "Ankara Esenboğa Airport", "Ankara", "Turkey", "TR", 40.1281, 32.9951, "Europe/Istanbul"),
        ("AYT", "Antalya Airport", "Antalya", "Turkey", "TR", 36.8987, 30.8005, "Europe/Istanbul"),
        
        # === THAILAND ===
        ("BKK", "Suvarnabhumi Airport", "Bangkok", "Thailand", "TH", 13.6811, 100.7475, "Asia/Bangkok"),
        ("DMK", "Don Mueang International Airport", "Bangkok", "Thailand", "TH", 13.9126, 100.6068, "Asia/Bangkok"),
        ("HKT", "Phuket International Airport", "Phuket", "Thailand", "TH", 8.1132, 98.3169, "Asia/Bangkok"),
        ("USM", "Samui Airport", "Koh Samui", "Thailand", "TH", 9.5478, 100.0622, "Asia/Bangkok"),
        
        # === JAPAN ===
        ("NRT", "Narita International Airport", "Tokyo", "Japan", "JP", 35.7647, 140.3863, "Asia/Tokyo"),
        ("HND", "Tokyo Haneda Airport", "Tokyo", "Japan", "JP", 35.5494, 139.7798, "Asia/Tokyo"),
        ("KIX", "Kansai International Airport", "Osaka", "Japan", "JP", 34.4273, 135.2441, "Asia/Tokyo"),
        ("NGO", "Chubu Centrair International Airport", "Nagoya", "Japan", "JP", 34.8584, 136.8054, "Asia/Tokyo"),
        ("FUK", "Fukuoka Airport", "Fukuoka", "Japan", "JP", 33.5859, 130.4510, "Asia/Tokyo"),
        ("CTS", "New Chitose Airport", "Sapporo", "Japan", "JP", 42.7752, 141.6923, "Asia/Tokyo"),
        
        # === SOUTH KOREA ===
        ("ICN", "Incheon International Airport", "Seoul", "South Korea", "KR", 37.4602, 126.4407, "Asia/Seoul"),
        ("PUS", "Gimhae International Airport", "Busan", "South Korea", "KR", 35.1794, 128.9382, "Asia/Seoul"),
        
        # === CHINA ===
        ("PEK", "Beijing Capital International Airport", "Beijing", "China", "CN", 40.0799, 116.6031, "Asia/Shanghai"),
        ("PVG", "Shanghai Pudong International Airport", "Shanghai", "China", "CN", 31.1443, 121.8083, "Asia/Shanghai"),
        ("CAN", "Guangzhou Baiyun International Airport", "Guangzhou", "China", "CN", 23.3924, 113.2990, "Asia/Shanghai"),
        ("SZX", "Shenzhen Bao'an International Airport", "Shenzhen", "China", "CN", 22.6393, 113.8106, "Asia/Shanghai"),
        ("CTU", "Chengdu Shuangliu International Airport", "Chengdu", "China", "CN", 30.5785, 103.9471, "Asia/Shanghai"),
        ("HKG", "Hong Kong International Airport", "Hong Kong", "China", "CN", 22.3080, 113.9185, "Asia/Hong_Kong"),
        ("TPE", "Taiwan Taoyuan International Airport", "Taipei", "Taiwan", "TW", 25.0797, 121.2342, "Asia/Taipei"),
        
        # === SINGAPORE ===
        ("SIN", "Singapore Changi Airport", "Singapore", "Singapore", "SG", 1.3644, 103.9915, "Asia/Singapore"),
        
        # === MALAYSIA ===
        ("KUL", "Kuala Lumpur International Airport", "Kuala Lumpur", "Malaysia", "MY", 2.7456, 101.7099, "Asia/Kuala_Lumpur"),
        
        # === INDONESIA ===
        ("CGK", "Soekarno-Hatta International Airport", "Jakarta", "Indonesia", "ID", -6.1256, 106.6558, "Asia/Jakarta"),
        ("DPS", "Ngurah Rai International Airport", "Bali", "Indonesia", "ID", -8.7482, 115.1670, "Asia/Makassar"),
        
        # === PHILIPPINES ===
        ("MNL", "Ninoy Aquino International Airport", "Manila", "Philippines", "PH", 14.5086, 121.0197, "Asia/Manila"),
        
        # === VIETNAM ===
        ("SGN", "Tan Son Nhat International Airport", "Ho Chi Minh City", "Vietnam", "VN", 10.8188, 106.6520, "Asia/Ho_Chi_Minh"),
        ("HAN", "Noi Bai International Airport", "Hanoi", "Vietnam", "VN", 21.2211, 105.8072, "Asia/Ho_Chi_Minh"),
        
        # === UNITED ARAB EMIRATES ===
        ("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates", "AE", 25.2532, 55.3657, "Asia/Dubai"),
        ("AUH", "Abu Dhabi International Airport", "Abu Dhabi", "United Arab Emirates", "AE", 24.4330, 54.6511, "Asia/Dubai"),
        
        # === QATAR ===
        ("DOH", "Hamad International Airport", "Doha", "Qatar", "QA", 25.2611, 51.5651, "Asia/Qatar"),
        
        # === SAUDI ARABIA ===
        ("RUH", "King Khalid International Airport", "Riyadh", "Saudi Arabia", "SA", 24.9576, 46.6988, "Asia/Riyadh"),
        ("JED", "King Abdulaziz International Airport", "Jeddah", "Saudi Arabia", "SA", 21.6796, 39.1565, "Asia/Riyadh"),
        
        # === AUSTRALIA ===
        ("SYD", "Sydney Kingsford Smith Airport", "Sydney", "Australia", "AU", -33.9399, 151.1753, "Australia/Sydney"),
        ("MEL", "Melbourne Airport", "Melbourne", "Australia", "AU", -37.6690, 144.8410, "Australia/Melbourne"),
        ("BNE", "Brisbane Airport", "Brisbane", "Australia", "AU", -27.3842, 153.1171, "Australia/Brisbane"),
        ("CNS", "Cairns Airport", "Cairns", "Australia", "AU", -16.8858, 145.7556, "Australia/Brisbane"),
        ("PER", "Perth Airport", "Perth", "Australia", "AU", -31.9403, 115.9670, "Australia/Perth"),
        ("ADL", "Adelaide Airport", "Adelaide", "Australia", "AU", -34.9455, 138.5306, "Australia/Adelaide"),
        ("DRW", "Darwin International Airport", "Darwin", "Australia", "AU", -12.4147, 130.8767, "Australia/Darwin"),
        
        # === NEW ZEALAND ===
        ("AKL", "Auckland Airport", "Auckland", "New Zealand", "NZ", -37.0082, 174.7850, "Pacific/Auckland"),
        ("WLG", "Wellington Airport", "Wellington", "New Zealand", "NZ", -41.3272, 174.8053, "Pacific/Auckland"),
        
        # === BRAZIL ===
        ("GRU", "São Paulo-Guarulhos International Airport", "São Paulo", "Brazil", "BR", -23.4321, -46.4692, "America/Sao_Paulo"),
        ("GIG", "Rio de Janeiro-Galeão International Airport", "Rio de Janeiro", "Brazil", "BR", -22.8089, -43.2436, "America/Sao_Paulo"),
        ("BSB", "Brasília International Airport", "Brasília", "Brazil", "BR", -15.8697, -47.9208, "America/Sao_Paulo"),
        ("FOR", "Pinto Martins International Airport", "Fortaleza", "Brazil", "BR", -3.7763, -38.5326, "America/Fortaleza"),
        
        # === ARGENTINA ===
        ("EZE", "Ministro Pistarini International Airport", "Buenos Aires", "Argentina", "AR", -34.8222, -58.5358, "America/Argentina/Buenos_Aires"),
        ("COR", "Ingeniero Ambrosio L.V. Taravella International Airport", "Córdoba", "Argentina", "AR", -31.3236, -64.2080, "America/Argentina/Cordoba"),
        ("MDZ", "Governor Francisco Gabrielli International Airport", "Mendoza", "Argentina", "AR", -32.8317, -68.7928, "America/Argentina/Mendoza"),
        
        # === MEXICO ===
        ("MEX", "Mexico City International Airport", "Mexico City", "Mexico", "MX", 19.4363, -99.0721, "America/Mexico_City"),
        ("CUN", "Cancún International Airport", "Cancún", "Mexico", "MX", 21.0365, -86.8770, "America/Cancun"),
        ("GDL", "Miguel Hidalgo y Costilla International Airport", "Guadalajara", "Mexico", "MX", 20.5218, -103.3112, "America/Mexico_City"),
        ("MTY", "General Mariano Escobedo International Airport", "Monterrey", "Mexico", "MX", 25.7785, -100.1069, "America/Monterrey"),
        
        # === CANADA ===
        ("YYZ", "Toronto Pearson International Airport", "Toronto", "Canada", "CA", 43.6772, -79.6306, "America/Toronto"),
        ("YVR", "Vancouver International Airport", "Vancouver", "Canada", "CA", 49.1947, -123.1792, "America/Vancouver"),
        ("YUL", "Montréal-Trudeau International Airport", "Montreal", "Canada", "CA", 45.4577, -73.7497, "America/Toronto"),
        ("YYC", "Calgary International Airport", "Calgary", "Canada", "CA", 51.1215, -114.0076, "America/Edmonton"),
        
        # === SOUTH AFRICA ===
        ("JNB", "O. R. Tambo International Airport", "Johannesburg", "South Africa", "ZA", -26.1367, 28.2411, "Africa/Johannesburg"),
        ("CPT", "Cape Town International Airport", "Cape Town", "South Africa", "ZA", -33.9648, 18.6017, "Africa/Johannesburg"),
        
        # === EGYPT ===
        ("CAI", "Cairo International Airport", "Cairo", "Egypt", "EG", 30.1219, 31.4056, "Africa/Cairo"),
        ("HRG", "Hurghada International Airport", "Hurghada", "Egypt", "EG", 27.1783, 33.7994, "Africa/Cairo"),
        ("LXR", "Luxor International Airport", "Luxor", "Egypt", "EG", 25.6710, 32.7066, "Africa/Cairo"),
        
        # === MOROCCO ===
        ("CMN", "Mohammed V International Airport", "Casablanca", "Morocco", "MA", 33.3675, -7.5899, "Africa/Casablanca"),
        ("RAK", "Marrakech Menara Airport", "Marrakech", "Morocco", "MA", 31.6069, -8.0369, "Africa/Casablanca"),
        
        # === ISRAEL ===
        ("TLV", "Ben Gurion Airport", "Tel Aviv", "Israel", "IL", 32.0114, 34.8867, "Asia/Jerusalem"),
        
        # === ICELAND ===
        ("KEF", "Keflavík International Airport", "Reykjavik", "Iceland", "IS", 63.9850, -22.6056, "Atlantic/Reykjavik"),
        
        # === IRELAND ===
        ("DUB", "Dublin Airport", "Dublin", "Ireland", "IE", 53.4264, -6.2499, "Europe/Dublin"),
        
        # === DENMARK ===
        ("CPH", "Copenhagen Airport", "Copenhagen", "Denmark", "DK", 55.6180, 12.6561, "Europe/Copenhagen"),
        
        # === SWEDEN ===
        ("ARN", "Stockholm Arlanda Airport", "Stockholm", "Sweden", "SE", 59.6519, 17.9186, "Europe/Stockholm"),
        
        # === NORWAY ===
        ("OSL", "Oslo Gardermoen Airport", "Oslo", "Norway", "NO", 60.1939, 11.1004, "Europe/Oslo"),
        
        # === CZECH REPUBLIC ===
        ("PRG", "Václav Havel Airport Prague", "Prague", "Czech Republic", "CZ", 50.1009, 14.2633, "Europe/Prague"),
        
        # === HUNGARY ===
        ("BUD", "Budapest Ferenc Liszt International Airport", "Budapest", "Hungary", "HU", 47.4390, 19.2618, "Europe/Budapest"),
        
        # === POLAND ===
        ("WAW", "Warsaw Chopin Airport", "Warsaw", "Poland", "PL", 52.1657, 20.9671, "Europe/Warsaw"),
        
        # === CROATIA ===
        ("DBV", "Dubrovnik Airport", "Dubrovnik", "Croatia", "HR", 42.5614, 18.2682, "Europe/Zagreb"),
        
        # === RUSSIA ===
        ("SVO", "Sheremetyevo International Airport", "Moscow", "Russia", "RU", 55.9726, 37.4146, "Europe/Moscow"),
        
        # === MALDIVES ===
        ("MLE", "Velana International Airport", "Malé", "Maldives", "MV", 4.1917, 73.5289, "Indian/Maldives"),
        
        # === SRI LANKA ===
        ("CMB", "Bandaranaike International Airport", "Colombo", "Sri Lanka", "LK", 7.1759, 79.8842, "Asia/Colombo"),
        
        # === CAMBODIA ===
        ("PNH", "Phnom Penh International Airport", "Phnom Penh", "Cambodia", "KH", 11.5466, 104.8441, "Asia/Phnom_Penh"),
        ("REP", "Siem Reap International Airport", "Siem Reap", "Cambodia", "KH", 13.4107, 103.8128, "Asia/Phnom_Penh"),
        
        # === LAOS ===
        ("VTE", "Wattay International Airport", "Vientiane", "Laos", "LA", 17.9883, 102.5633, "Asia/Vientiane"),
        ("LPQ", "Luang Prabang International Airport", "Luang Prabang", "Laos", "LA", 19.8979, 102.1608, "Asia/Vientiane"),
        
        # === MYANMAR ===
        ("RGN", "Yangon International Airport", "Yangon", "Myanmar", "MM", 16.9073, 96.1332, "Asia/Yangon"),
        ("MDL", "Mandalay International Airport", "Mandalay", "Myanmar", "MM", 21.7022, 95.9779, "Asia/Yangon"),
        
        # === OMAN ===
        ("MCT", "Muscat International Airport", "Muscat", "Oman", "OM", 23.5933, 58.2844, "Asia/Muscat"),
        ("SLL", "Salalah Airport", "Salalah", "Oman", "OM", 17.0387, 54.0913, "Asia/Muscat"),
        
        # === JORDAN ===
        ("AMM", "Queen Alia International Airport", "Amman", "Jordan", "JO", 31.7226, 35.9932, "Asia/Amman"),
        ("AQJ", "King Hussein International Airport", "Aqaba", "Jordan", "JO", 29.6116, 35.0181, "Asia/Amman"),
        
        # === LEBANON ===
        ("BEY", "Beirut-Rafic Hariri International Airport", "Beirut", "Lebanon", "LB", 33.8209, 35.4883, "Asia/Beirut"),
        
        # === KENYA ===
        ("NBO", "Jomo Kenyatta International Airport", "Nairobi", "Kenya", "KE", -1.3192, 36.9275, "Africa/Nairobi"),
        ("MBA", "Moi International Airport", "Mombasa", "Kenya", "KE", -4.0348, 39.5943, "Africa/Nairobi"),
        
        # === TANZANIA ===
        ("DAR", "Julius Nyerere International Airport", "Dar es Salaam", "Tanzania", "TZ", -6.8781, 39.2026, "Africa/Dar_es_Salaam"),
        ("JRO", "Kilimanjaro International Airport", "Kilimanjaro", "Tanzania", "TZ", -3.4294, 37.0745, "Africa/Dar_es_Salaam"),
        ("ZNZ", "Abeid Amani Karume International Airport", "Zanzibar", "Tanzania", "TZ", -6.2220, 39.2249, "Africa/Dar_es_Salaam"),
        
        # === MAURITIUS ===
        ("MRU", "Sir Seewoosagur Ramgoolam International Airport", "Port Louis", "Mauritius", "MU", -20.4302, 57.6836, "Indian/Mauritius"),
        
        # === SEYCHELLES ===
        ("SEZ", "Seychelles International Airport", "Mahé", "Seychelles", "SC", -4.6743, 55.5218, "Indian/Mahe"),
        
        # === ALBANIA ===
        ("TIA", "Tirana International Airport", "Tirana", "Albania", "AL", 41.4147, 19.7206, "Europe/Tirane"),
        
        # === MONTENEGRO ===
        ("TGD", "Podgorica Airport", "Podgorica", "Montenegro", "ME", 42.3594, 19.2519, "Europe/Podgorica"),
        ("TIV", "Tivat Airport", "Tivat", "Montenegro", "ME", 42.4047, 18.7233, "Europe/Podgorica"),
        
        # === SLOVENIA ===
        ("LJU", "Ljubljana Jože Pučnik Airport", "Ljubljana", "Slovenia", "SI", 46.2237, 14.4576, "Europe/Ljubljana"),
        
        # === CHILE ===
        ("SCL", "Arturo Merino Benítez International Airport", "Santiago", "Chile", "CL", -33.3930, -70.7858, "America/Santiago"),
        ("PMC", "El Tepual Airport", "Puerto Montt", "Chile", "CL", -41.4389, -73.0940, "America/Santiago"),
        
        # === PERU ===
        ("LIM", "Jorge Chávez International Airport", "Lima", "Peru", "PE", -12.0219, -77.1143, "America/Lima"),
        ("CUZ", "Alejandro Velasco Astete International Airport", "Cusco", "Peru", "PE", -13.5357, -71.9388, "America/Lima"),
        
        # === ECUADOR ===
        ("UIO", "Mariscal Sucre International Airport", "Quito", "Ecuador", "EC", -0.1411, -78.4882, "America/Guayaquil"),
        ("GYE", "José Joaquín de Olmedo International Airport", "Guayaquil", "Ecuador", "EC", -2.1574, -79.8836, "America/Guayaquil"),
        ("GPS", "Seymour Airport", "Galapagos", "Ecuador", "EC", -0.4537, -90.2659, "Pacific/Galapagos"),
        
        # === COSTA RICA ===
        ("SJO", "Juan Santamaría International Airport", "San José", "Costa Rica", "CR", 9.9939, -84.2088, "America/Costa_Rica"),
        ("LIR", "Daniel Oduber Quirós International Airport", "Liberia", "Costa Rica", "CR", 10.5933, -85.5444, "America/Costa_Rica"),
        
        # === PANAMA ===
        ("PTY", "Tocumen International Airport", "Panama City", "Panama", "PA", 9.0714, -79.3835, "America/Panama"),
        
        # === JAMAICA ===
        ("MBJ", "Sangster International Airport", "Montego Bay", "Jamaica", "JM", 18.5037, -77.9134, "America/Jamaica"),
        ("KIN", "Norman Manley International Airport", "Kingston", "Jamaica", "JM", 17.9356, -76.7875, "America/Jamaica"),
        
        # === BARBADOS ===
        ("BGI", "Grantley Adams International Airport", "Bridgetown", "Barbados", "BB", 13.0746, -59.4925, "America/Barbados"),
        
        # === DOMINICAN REPUBLIC ===
        ("PUJ", "Punta Cana International Airport", "Punta Cana", "Dominican Republic", "DO", 18.5674, -68.3634, "America/Santo_Domingo"),
        ("SDQ", "Las Américas International Airport", "Santo Domingo", "Dominican Republic", "DO", 18.4297, -69.6689, "America/Santo_Domingo"),
        
        # === FIJI ===
        ("NAN", "Nadi International Airport", "Nadi", "Fiji", "FJ", -17.7554, 177.4434, "Pacific/Fiji"),
        
        # === NEW CALEDONIA ===
        ("NOU", "La Tontouta International Airport", "Nouméa", "New Caledonia", "NC", -22.0146, 166.2130, "Pacific/Noumea"),
        
        # === FRENCH POLYNESIA ===
        ("PPT", "Faa'a International Airport", "Papeete", "French Polynesia", "PF", -17.5567, -149.6114, "Pacific/Tahiti"),
        
        # === BAHRAIN ===
        ("BAH", "Bahrain International Airport", "Manama", "Bahrain", "BH", 26.2708, 50.6336, "Asia/Bahrain"),
        
        # === KUWAIT ===
        ("KWI", "Kuwait International Airport", "Kuwait City", "Kuwait", "KW", 29.2266, 47.9689, "Asia/Kuwait"),
        
        # === BANGLADESH ===
        ("DAC", "Hazrat Shahjalal International Airport", "Dhaka", "Bangladesh", "BD", 23.8433, 90.3978, "Asia/Dhaka"),
        
        # === NEPAL ===
        ("KTM", "Tribhuvan International Airport", "Kathmandu", "Nepal", "NP", 27.6966, 85.3591, "Asia/Kathmandu"),
        
        # === BHUTAN ===
        ("PBH", "Paro International Airport", "Paro", "Bhutan", "BT", 27.4032, 89.4246, "Asia/Thimphu"),
        
        # === MYANMAR (additional) ===
        ("NYT", "Naypyidaw International Airport", "Naypyidaw", "Myanmar", "MM", 19.6233, 96.2008, "Asia/Yangon"),
        
        # === MALAYSIA (additional) ===
        ("PEN", "Penang International Airport", "Penang", "Malaysia", "MY", 5.2971, 100.2769, "Asia/Kuala_Lumpur"),
        ("LGK", "Langkawi International Airport", "Langkawi", "Malaysia", "MY", 6.3297, 99.7286, "Asia/Kuala_Lumpur"),
        
        # === INDONESIA (additional) ===
        ("UPG", "Sultan Hasanuddin International Airport", "Makassar", "Indonesia", "ID", -5.0616, 119.5542, "Asia/Makassar"),
        ("SUB", "Juanda International Airport", "Surabaya", "Indonesia", "ID", -7.3798, 112.7869, "Asia/Jakarta"),
        
        # === PHILIPPINES (additional) ===
        ("CEB", "Mactan-Cebu International Airport", "Cebu", "Philippines", "PH", 10.3073, 123.9794, "Asia/Manila"),
        ("DVO", "Francisco Bangoy International Airport", "Davao", "Philippines", "PH", 7.1256, 125.6458, "Asia/Manila"),
        
        # === UNITED KINGDOM (additional) ===
        ("STN", "London Stansted Airport", "London", "United Kingdom", "GB", 51.8860, 0.2389, "Europe/London"),
        ("BHX", "Birmingham Airport", "Birmingham", "United Kingdom", "GB", 52.4539, -1.7480, "Europe/London"),
        ("GLA", "Glasgow Airport", "Glasgow", "United Kingdom", "GB", 55.8719, -4.4331, "Europe/London"),
        
        # === RUSSIA (additional) ===
        ("LED", "Pulkovo Airport", "Saint Petersburg", "Russia", "RU", 59.8003, 30.2625, "Europe/Moscow"),
        
        # === POLAND (additional) ===
        ("KRK", "John Paul II International Airport", "Kraków", "Poland", "PL", 50.0777, 19.7848, "Europe/Warsaw"),
        ("GDN", "Gdańsk Lech Wałęsa Airport", "Gdańsk", "Poland", "PL", 54.3776, 18.4662, "Europe/Warsaw"),
        
        # === ROMANIA ===
        ("OTP", "Henri Coandă International Airport", "Bucharest", "Romania", "RO", 44.5711, 26.0858, "Europe/Bucharest"),
        
        # === BULGARIA ===
        ("SOF", "Sofia Airport", "Sofia", "Bulgaria", "BG", 42.6952, 23.4062, "Europe/Sofia"),
        
        # === SERBIA ===
        ("BEG", "Belgrade Nikola Tesla Airport", "Belgrade", "Serbia", "RS", 44.8184, 20.3092, "Europe/Belgrade"),
        
        # === GEORGIA ===
        ("TBS", "Tbilisi International Airport", "Tbilisi", "Georgia", "GE", 41.6692, 44.9547, "Asia/Tbilisi"),
        
        # === ARMENIA ===
        ("EVN", "Zvartnots International Airport", "Yerevan", "Armenia", "AM", 40.1473, 44.3959, "Asia/Yerevan"),
        
        # === AZERBAIJAN ===
        ("GYD", "Heydar Aliyev International Airport", "Baku", "Azerbaijan", "AZ", 40.4675, 50.0467, "Asia/Baku"),
        
        # === KAZAKHSTAN ===
        ("ALA", "Almaty International Airport", "Almaty", "Kazakhstan", "KZ", 43.3522, 77.0405, "Asia/Almaty"),
        
        # === UZBEKISTAN ===
        ("TAS", "Tashkent International Airport", "Tashkent", "Uzbekistan", "UZ", 41.2575, 69.2811, "Asia/Tashkent"),
        
        # === COLOMBIA ===
        ("BOG", "El Dorado International Airport", "Bogotá", "Colombia", "CO", 4.7016, -74.1469, "America/Bogota"),
        ("MDE", "José María Córdova International Airport", "Medellín", "Colombia", "CO", 6.1644, -75.4231, "America/Bogota"),
        
        # === VENEZUELA ===
        ("CCS", "Simón Bolívar International Airport", "Caracas", "Venezuela", "VE", 10.6012, -66.9912, "America/Caracas"),
        
        # === URUGUAY ===
        ("MVD", "Carrasco International Airport", "Montevideo", "Uruguay", "UY", -34.8384, -56.0308, "America/Montevideo"),
        
        # === PARAGUAY ===
        ("ASU", "Silvio Pettirossi International Airport", "Asunción", "Paraguay", "PY", -25.2397, -57.5192, "America/Asuncion"),
        
        # === BOLIVIA ===
        ("LPB", "El Alto International Airport", "La Paz", "Bolivia", "BO", -16.5133, -68.1923, "America/La_Paz"),
        
        # === URUGUAY (additional) ===
        ("PDP", "Capitan Corbeta CA Curbelo International Airport", "Punta del Este", "Uruguay", "UY", -34.8551, -55.0942, "America/Montevideo"),
    ]


def get_popular_indian_airports():
    """Get list of popular Indian tourist destination airports - includes cities mapped to nearest airports"""
    return [
        # Major metropolitan airports
        ("DEL", "Indira Gandhi International Airport", "New Delhi", "India", "IN", 28.5566, 77.1000, "Asia/Kolkata"),
        ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India", "IN", 19.0896, 72.8656, "Asia/Kolkata"),
        ("BLR", "Kempegowda International Airport", "Bangalore", "India", "IN", 13.1986, 77.7066, "Asia/Kolkata"),
        ("MAA", "Chennai International Airport", "Chennai", "India", "IN", 12.9944, 80.1806, "Asia/Kolkata"),
        ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India", "IN", 17.2403, 78.4294, "Asia/Kolkata"),
        ("CCU", "Netaji Subhash Chandra Bose International Airport", "Kolkata", "India", "IN", 22.6547, 88.4467, "Asia/Kolkata"),
        ("PNQ", "Pune Airport", "Pune", "India", "IN", 18.5822, 73.9197, "Asia/Kolkata"),
        
        # Punjab & Haryana region (city aliases handled separately)
        ("IXC", "Chandigarh Airport", "Chandigarh", "India", "IN", 30.6735, 76.7885, "Asia/Kolkata"),
        ("ATQ", "Sri Guru Ram Dass Jee International Airport", "Amritsar", "India", "IN", 31.7096, 74.7973, "Asia/Kolkata"),
        ("LUH", "Ludhiana Airport", "Ludhiana", "India", "IN", 30.8547, 75.9523, "Asia/Kolkata"),
        ("PGH", "Sahnewal Airport", "Patiala", "India", "IN", 30.6695, 76.6797, "Asia/Kolkata"),
        
        # Popular tourist destinations - Goa (city aliases handled separately)
        ("GOI", "Dabolim Airport", "Goa", "India", "IN", 15.3808, 73.8314, "Asia/Kolkata"),
        
        # Rajasthan - heritage destinations (city aliases handled separately)
        ("JAI", "Jaipur International Airport", "Jaipur", "India", "IN", 26.8242, 75.8017, "Asia/Kolkata"),
        ("UDR", "Maharana Pratap Airport", "Udaipur", "India", "IN", 24.6177, 73.8961, "Asia/Kolkata"),
        ("JDH", "Jodhpur Airport", "Jodhpur", "India", "IN", 26.2511, 73.0489, "Asia/Kolkata"),
        ("BKB", "Nal Airport", "Bikaner", "India", "IN", 28.0706, 73.2072, "Asia/Kolkata"),
        ("JSA", "Jaisalmer Airport", "Jaisalmer", "India", "IN", 26.8887, 70.8650, "Asia/Kolkata"),
        
        # Gujarat - business and tourism
        ("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "India", "IN", 23.0772, 72.6347, "Asia/Kolkata"),
        ("BDQ", "Vadodara Airport", "Vadodara", "India", "IN", 22.3362, 73.2263, "Asia/Kolkata"),
        ("STV", "Surat Airport", "Surat", "India", "IN", 21.1140, 72.7419, "Asia/Kolkata"),
        ("RAJ", "Rajkot Airport", "Rajkot", "India", "IN", 22.3092, 70.7795, "Asia/Kolkata"),
        ("BHJ", "Bhuj Airport", "Bhuj", "India", "IN", 23.2878, 69.6702, "Asia/Kolkata"),
        ("IXY", "Kandla Airport", "Kandla", "India", "IN", 23.1127, 70.1003, "Asia/Kolkata"),
        ("PBD", "Porbandar Airport", "Porbandar", "India", "IN", 21.6487, 69.6572, "Asia/Kolkata"),
        
        # Kerala - popular tourist state (city aliases handled separately)
        ("COK", "Cochin International Airport", "Kochi", "India", "IN", 9.9312, 76.2673, "Asia/Kolkata"),
        ("TRV", "Trivandrum International Airport", "Thiruvananthapuram", "India", "IN", 8.4821, 76.9200, "Asia/Kolkata"),
        ("CCJ", "Calicut International Airport", "Kozhikode", "India", "IN", 11.1368, 75.9553, "Asia/Kolkata"),
        ("CNN", "Kannur International Airport", "Kannur", "India", "IN", 11.9186, 75.5472, "Asia/Kolkata"),
        
        # Tamil Nadu - temples and beaches (city aliases handled separately)
        ("CJB", "Coimbatore International Airport", "Coimbatore", "India", "IN", 11.0290, 77.0434, "Asia/Kolkata"),
        ("IXM", "Madurai Airport", "Madurai", "India", "IN", 9.8345, 78.0934, "Asia/Kolkata"),
        ("TRZ", "Tiruchirapalli International Airport", "Trichy", "India", "IN", 10.7654, 78.7097, "Asia/Kolkata"),
        ("PNY", "Puducherry Airport", "Puducherry", "India", "IN", 11.9680, 79.8120, "Asia/Kolkata"),
        ("TUY", "Thoothukudi Airport", "Tuticorin", "India", "IN", 8.7244, 78.0250, "Asia/Kolkata"),
        
        # Andaman & Nicobar
        ("IXZ", "Veer Savarkar International Airport", "Port Blair", "India", "IN", 11.6412, 92.7297, "Asia/Kolkata"),
        
        # West Bengal - cultural destinations (Kolkata already listed above, city aliases handled separately)
        ("IXB", "Bagdogra Airport", "Bagdogra", "India", "IN", 26.6812, 88.3286, "Asia/Kolkata"),
        ("RDP", "Durgapur Airport", "Durgapur", "India", "IN", 23.6225, 87.2430, "Asia/Kolkata"),
        
        # Himachal Pradesh - hill stations (city aliases handled separately)
        ("IXJ", "Jammu Airport", "Jammu", "India", "IN", 32.6892, 74.8374, "Asia/Kolkata"),
        ("KUU", "Kullu Manali Airport", "Kullu", "India", "IN", 31.8769, 77.1544, "Asia/Kolkata"),
        ("SLV", "Shimla Airport", "Shimla", "India", "IN", 31.0818, 77.0681, "Asia/Kolkata"),
        ("DHM", "Gaggal Airport", "Dharamshala", "India", "IN", 32.1651, 76.2634, "Asia/Kolkata"),
        ("SXR", "Sheikh ul-Alam Airport", "Srinagar", "India", "IN", 33.9871, 74.7742, "Asia/Kolkata"),
        ("IXL", "Leh Kushok Bakula Rimpochee Airport", "Leh", "India", "IN", 34.1359, 77.5465, "Asia/Kolkata"),
        
        # Uttarakhand - spiritual and adventure tourism (city aliases handled separately)
        ("DED", "Jolly Grant Airport", "Dehradun", "India", "IN", 30.1897, 78.1803, "Asia/Kolkata"),
        ("PGH", "Pantnagar Airport", "Pantnagar", "India", "IN", 29.0334, 79.4737, "Asia/Kolkata"),
        
        # Madhya Pradesh - heritage sites (city aliases handled separately)
        ("IDR", "Devi Ahilya Bai Holkar Airport", "Indore", "India", "IN", 22.7218, 75.8011, "Asia/Kolkata"),
        ("BHO", "Raja Bhoj Airport", "Bhopal", "India", "IN", 23.2877, 77.3376, "Asia/Kolkata"),
        ("JLR", "Jabalpur Airport", "Jabalpur", "India", "IN", 23.1778, 80.0520, "Asia/Kolkata"),
        ("GWL", "Gwalior Airport", "Gwalior", "India", "IN", 26.2933, 78.2278, "Asia/Kolkata"),
        ("HBX", "Khajuraho Airport", "Khajuraho", "India", "IN", 24.8172, 79.9186, "Asia/Kolkata"),
        
        # Chhattisgarh
        ("RPR", "Swami Vivekananda Airport", "Raipur", "India", "IN", 21.1804, 81.7388, "Asia/Kolkata"),
        
        # Uttar Pradesh - Taj Mahal and spiritual sites (city aliases handled separately)
        ("AGR", "Agra Airport", "Agra", "India", "IN", 27.1558, 77.9608, "Asia/Kolkata"),
        ("VNS", "Lal Bahadur Shastri Airport", "Varanasi", "India", "IN", 25.4484, 82.8592, "Asia/Kolkata"),
        ("LKO", "Chaudhary Charan Singh International Airport", "Lucknow", "India", "IN", 26.7606, 80.8893, "Asia/Kolkata"),
        ("IXD", "Allahabad Airport", "Allahabad", "India", "IN", 25.4405, 81.7339, "Asia/Kolkata"),
        ("KNU", "Kanpur Airport", "Kanpur", "India", "IN", 26.4041, 80.3641, "Asia/Kolkata"),
        
        # Odisha - temples and beaches (city aliases handled separately)
        ("BBI", "Biju Patnaik International Airport", "Bhubaneswar", "India", "IN", 20.2444, 85.8178, "Asia/Kolkata"),
        
        # Assam - wildlife and tea gardens (city aliases handled separately)
        ("GAU", "Lokpriya Gopinath Bordoloi International Airport", "Guwahati", "India", "IN", 26.1061, 91.5859, "Asia/Kolkata"),
        ("DIB", "Dibrugarh Airport", "Dibrugarh", "India", "IN", 27.4839, 95.0169, "Asia/Kolkata"),
        ("IXS", "Silchar Airport", "Silchar", "India", "IN", 24.9129, 92.9787, "Asia/Kolkata"),
        
        # Northeast states
        ("IMF", "Imphal Airport", "Imphal", "India", "IN", 24.7600, 93.8967, "Asia/Kolkata"),
        ("AJL", "Lengpui Airport", "Aizawl", "India", "IN", 23.8406, 92.6197, "Asia/Kolkata"),
        ("AGX", "Agartala Airport", "Agartala", "India", "IN", 23.8869, 91.2404, "Asia/Kolkata"),
        
        # Andhra Pradesh & Telangana - temples
        ("VGA", "Vijayawada Airport", "Vijayawada", "India", "IN", 16.5304, 80.7968, "Asia/Kolkata"),
        ("TIR", "Tirupati Airport", "Tirupati", "India", "IN", 13.6325, 79.5433, "Asia/Kolkata"),
        ("VTZ", "Visakhapatnam Airport", "Visakhapatnam", "India", "IN", 17.7211, 83.2245, "Asia/Kolkata"),
        ("VTZ", "Visakhapatnam Airport", "Vizag", "India", "IN", 17.7211, 83.2245, "Asia/Kolkata"),
        ("RJA", "Rajahmundry Airport", "Rajahmundry", "India", "IN", 17.1104, 81.8182, "Asia/Kolkata"),
        
        # Karnataka - tech and heritage (city aliases handled separately)
        ("IXG", "Belgaum Airport", "Belgaum", "India", "IN", 15.8593, 74.6183, "Asia/Kolkata"),
        ("MYQ", "Mysore Airport", "Mysore", "India", "IN", 12.2300, 76.6558, "Asia/Kolkata"),
        ("IXE", "Mangalore International Airport", "Mangalore", "India", "IN", 12.9612, 74.8900, "Asia/Kolkata"),
        ("VGA", "Hubli Airport", "Hubli", "India", "IN", 15.3617, 75.0849, "Asia/Kolkata"),
        
        # Bihar - spiritual tourism (city aliases handled separately)
        ("PAT", "Jay Prakash Narayan Airport", "Patna", "India", "IN", 25.5913, 85.0880, "Asia/Kolkata"),
        ("GAY", "Gaya Airport", "Gaya", "India", "IN", 24.7473, 84.9512, "Asia/Kolkata"),
        
        # Jharkhand
        ("IXR", "Birsa Munda Airport", "Ranchi", "India", "IN", 23.3144, 85.3217, "Asia/Kolkata"),
    ]


def populate_from_csv(csv_path: str = None):
    """Populate database from CSV file or download from public source"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM airports")
    count = cursor.fetchone()[0]
    
    if count > 100:
        print(f"✅ [AIRPORT-DB] Database already has {count} airports")
        # Still ensure popular airports are present even if database exists
        print("🔍 [AIRPORT-DB] Ensuring popular airports are present...")
        
        # Ensure popular international airports are present
        popular_international = get_popular_international_airports()
        cursor.executemany("""
            INSERT OR IGNORE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, popular_international)
        conn.commit()
        international_count = cursor.rowcount
        if international_count > 0:
            print(f"✅ [AIRPORT-DB] Added {international_count} popular international airports")
        
        # Ensure popular Indian airports are present
        popular_indian = get_popular_indian_airports()
        cursor.executemany("""
            INSERT OR IGNORE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, popular_indian)
        conn.commit()
        indian_count = cursor.rowcount
        if indian_count > 0:
            print(f"✅ [AIRPORT-DB] Added {indian_count} popular Indian airports")
        
        # Update counts
        cursor.execute("SELECT COUNT(*) FROM airports")
        final_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'IN'")
        india_count = cursor.fetchone()[0]
        print(f"📊 [AIRPORT-DB] Final: {final_count} total airports, {india_count} Indian airports")
        
        # If database has too many airports, it needs cleanup (will be done by delete_unpopular_airports in lifespan)
        if final_count > 200:
            print(f"⚠️ [AIRPORT-DB] Database has {final_count} airports - cleanup needed (will be cleaned on startup)")
        
        conn.close()
        return
    
    airports = []
    
    # If CSV path provided, use it
    if csv_path and os.path.exists(csv_path):
        print(f"📂 [AIRPORT-DB] Loading airports from local CSV: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8') as f:
            data = f.read()
        airports = parse_ourairports_csv(data)
    
    # Otherwise, download from public source
    else:
        print("🌐 [AIRPORT-DB] No local CSV found, downloading from public source...")
        csv_data, source = download_airports_data()
        
        if csv_data:
            if source == "openflights":
                airports = parse_openflights_csv(csv_data)
            else:
                airports = parse_ourairports_csv(csv_data)
        else:
            print("❌ [AIRPORT-DB] Failed to download airport data")
            conn.close()
            return
    
    if not airports:
        print("⚠️ [AIRPORT-DB] No airports found in data, using only popular airports")
        airports = []
    
    # For fresh database, ONLY add popular tourist destination airports
    # Don't add all downloaded airports - only popular ones to keep database clean
    print("🎯 [AIRPORT-DB] Fresh database - adding ONLY popular tourist destination airports")
    
    popular_international = get_popular_international_airports()
    popular_indian = get_popular_indian_airports()
    
    # Combine all popular airports - ignore downloaded data, only use curated list
    all_popular_airports = popular_international + popular_indian
    
    # Remove duplicates based on IATA code
    seen_codes = set()
    unique_airports = []
    for airport in all_popular_airports:
        code = airport[0]
        if code and code not in seen_codes:
            seen_codes.add(code)
            unique_airports.append(airport)
    
    print(f"📊 [AIRPORT-DB] Will add {len(unique_airports)} popular tourist destination airports only")
    print(f"   International: {len(popular_international)}, Indian: {len(popular_indian)}")
    print(f"   (Skipping {len(airports)} downloaded airports - only keeping popular ones)")
    
    # Insert only popular airports
    cursor.executemany("""
        INSERT OR IGNORE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, unique_airports)
    inserted = cursor.rowcount
    conn.commit()
    print(f"📝 [AIRPORT-DB] Inserted {inserted} popular airports")
    
    # Get final count
    cursor.execute("SELECT COUNT(*) FROM airports")
    final_count = cursor.fetchone()[0]
    
    # Check India airport count
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'IN'")
    india_count = cursor.fetchone()[0]
    print(f"📊 [AIRPORT-DB] Total airports: {final_count}, Indian airports: {india_count}")
    
    conn.close()
    print(f"✅ [AIRPORT-DB] Successfully populated {final_count} airports into database")


def ensure_popular_airports():
    """Ensure popular airports are always in the database (can be called anytime)"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added_count = 0
    
    # Add popular international airports
    popular_international = get_popular_international_airports()
    cursor.executemany("""
        INSERT OR IGNORE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, popular_international)
    conn.commit()
    international_count = cursor.rowcount
    added_count += international_count
    
    # Add popular Indian airports
    popular_indian = get_popular_indian_airports()
    cursor.executemany("""
        INSERT OR IGNORE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, popular_indian)
    conn.commit()
    indian_count = cursor.rowcount
    added_count += indian_count
    
    # Get final counts
    cursor.execute("SELECT COUNT(*) FROM airports")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'IN'")
    india_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ [AIRPORT-DB] Popular airports check complete - Added: {added_count}, Total: {total_count}, Indian: {india_count}")
    return added_count, total_count, india_count


def get_city_aliases():
    """Map city names to their nearest airport codes"""
    return {
        # Punjab & Haryana region - all use Chandigarh (IXC)
        'ambala': 'IXC',
        'panchkula': 'IXC',
        'mohali': 'IXC',
        'zirakpur': 'IXC',
        
        # Rajasthan
        'ajmer': 'JAI',
        'pushkar': 'JAI',
        'mount abu': 'UDR',
        
        # Kerala hill stations
        'munnar': 'COK',
        'thekkady': 'COK',
        'alleppey': 'COK',
        'alappuzha': 'COK',
        'ernakulam': 'COK',
        'kovalam': 'TRV',
        'varkala': 'TRV',
        
        # Tamil Nadu
        'ooty': 'CJB',
        'ootacamund': 'CJB',
        'udhagamandalam': 'CJB',
        'kodaikanal': 'CJB',
        'mahabalipuram': 'MAA',
        'pondicherry': 'MAA',
        'thanjavur': 'TRZ',
        'rameshwaram': 'IXM',
        
        # Uttarakhand
        'mussoorie': 'DED',
        'rishikesh': 'DED',
        'haridwar': 'DED',
        'nainital': 'PGH',
        
        # Himachal Pradesh
        'manali': 'KUU',
        'mcleod ganj': 'DHM',
        'dalhousie': 'DHM',
        
        # West Bengal & Sikkim
        'darjeeling': 'IXB',
        'gangtok': 'IXB',
        'kalimpong': 'IXB',
        'siliguri': 'IXB',
        
        # Uttar Pradesh
        'mathura': 'DEL',
        'vrindavan': 'DEL',
        'fatehpur sikri': 'AGR',
        'benares': 'VNS',
        'prayagraj': 'IXD',
        
        # Odisha
        'puri': 'BBI',
        'konark': 'BBI',
        
        # Goa
        'panaji': 'GOI',
        'margao': 'GOI',
        'panjim': 'GOI',
        
        # Assam & Northeast
        'shillong': 'GAU',
        'kaziranga': 'GAU',
        
        # Madhya Pradesh
        'ujjain': 'IDR',
        'mandu': 'IDR',
        
        # Karnataka
        'hampi': 'BLR',
        'coorg': 'IXE',
        'madikeri': 'IXE',
        
        # Bihar
        'bodhgaya': 'GAY',
        'bodh gaya': 'GAY',
    }


def get_airports(search_term: Optional[str] = None, limit: int = 500) -> List[Dict]:
    """Get airports from database with optional search - prioritizes Indian airports and handles city aliases"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search_term:
        # Case-insensitive search with improved matching
        search_term_upper = search_term.upper().strip()
        search_term_lower = search_term.lower().strip()
        search_pattern = f"%{search_term_upper}%"
        
        # Check city aliases with exact and partial matching
        city_aliases = get_city_aliases()
        
        # Strategy 1: Exact alias match
        if search_term_lower in city_aliases:
            airport_code = city_aliases[search_term_lower]
            print(f"🔍 [AIRPORT-DB] Found exact city alias: '{search_term}' → {airport_code}")
            cursor.execute("""
                SELECT code, name, city, country, country_code
                FROM airports
                WHERE code = ?
                LIMIT 1
            """, (airport_code,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['name'] = f"{result['name']} (nearest to {search_term})"
                conn.close()
                return [result]
        
        # Strategy 2: Fuzzy alias match (for typos like "amala" → "ambala", "munar" → "munnar")
        # First, apply common typo corrections
        typo_corrections = {
            'i': 'y',  # ooti → ooty
            'y': 'i',
            'ei': 'ee',
            'ee': 'ei',
        }
        search_variants = [search_term_lower]
        # Create variants with common typo fixes
        for old, new in typo_corrections.items():
            if old in search_term_lower:
                variant = search_term_lower.replace(old, new)
                search_variants.append(variant)
        
        # Use simple edit distance / character similarity
        if len(search_term_lower) >= 3:
            best_match = None
            best_score = 0
            
            for alias_city, airport_code in city_aliases.items():
                # Quick filter: must be within reasonable length difference
                len_diff = abs(len(search_term_lower) - len(alias_city))
                # Be more lenient for very short names (4 chars or less)
                max_len_diff = 1 if min(len(search_term_lower), len(alias_city)) <= 4 else 2
                if len_diff > max_len_diff:
                    continue
                
                # Calculate similarity using common character ratio
                # Check if any search variant matches exactly
                if alias_city in search_variants:
                    similarity = 1.0  # Perfect match via typo correction
                # Check if search term is substring
                elif search_term_lower in alias_city or alias_city in search_term_lower:
                    similarity = 0.9  # High score for substring matches
                else:
                    # Calculate character overlap
                    search_chars = set(search_term_lower)
                    alias_chars = set(alias_city)
                    common_chars = search_chars & alias_chars
                    total_chars = search_chars | alias_chars
                    similarity = len(common_chars) / len(total_chars) if total_chars else 0
                
                # Bonus for matching prefix (first 3 characters)
                if len(search_term_lower) >= 3 and len(alias_city) >= 3:
                    if search_term_lower[:3] == alias_city[:3]:
                        similarity += 0.2
                
                # Track best match
                if similarity > best_score and similarity >= 0.75:  # 75% threshold
                    best_score = similarity
                    best_match = (alias_city, airport_code)
            
            # If we found a good fuzzy match, use it
            if best_match:
                alias_city, airport_code = best_match
                print(f"🔍 [AIRPORT-DB] Found fuzzy city alias match: '{search_term}' ≈ '{alias_city}' (similarity: {best_score:.2f}) → {airport_code}")
                cursor.execute("""
                    SELECT code, name, city, country, country_code
                    FROM airports
                    WHERE code = ?
                    LIMIT 1
                """, (airport_code,))
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['name'] = f"{result['name']} (nearest to {alias_city})"
                    conn.close()
                    return [result]
        
        # Get popular Indian airport codes for prioritization
        popular_indian = get_popular_indian_airports()
        indian_codes = [airport[0] for airport in popular_indian]
        
        # Build SQL query safely - handle empty indian_codes
        if indian_codes:
            in_clause = ','.join(['?' for _ in indian_codes])
            sql_query = f"""
                SELECT code, name, city, country, country_code
                FROM airports
                WHERE 
                    UPPER(code) LIKE ? OR 
                    UPPER(name) LIKE ? OR 
                    UPPER(city) LIKE ? OR
                    UPPER(country) LIKE ? OR
                    code = ?
                ORDER BY 
                    CASE 
                        WHEN code = ? THEN 1
                        WHEN code IN ({in_clause}) THEN 2
                        WHEN country_code = 'IN' THEN 3
                        WHEN UPPER(code) LIKE ? THEN 4
                        WHEN UPPER(name) LIKE ? THEN 5
                        WHEN UPPER(city) LIKE ? THEN 6
                        ELSE 7
                    END,
                    CASE 
                        WHEN country_code = 'IN' THEN 1
                        ELSE 2
                    END,
                    name
                LIMIT ?
            """
            params = (
                search_pattern, search_pattern, search_pattern, search_pattern, search_term_upper,
                search_term_upper,
                *indian_codes,
                f"{search_term_upper}%",
                f"%{search_term_upper}%",
                f"%{search_term_upper}%",
                limit
            )
        else:
            # Fallback if no Indian codes available
            sql_query = """
                SELECT code, name, city, country, country_code
                FROM airports
                WHERE 
                    UPPER(code) LIKE ? OR 
                    UPPER(name) LIKE ? OR 
                    UPPER(city) LIKE ? OR
                    UPPER(country) LIKE ? OR
                    code = ?
                ORDER BY 
                    CASE 
                        WHEN code = ? THEN 1
                        WHEN country_code = 'IN' THEN 2
                        WHEN UPPER(code) LIKE ? THEN 3
                        WHEN UPPER(name) LIKE ? THEN 4
                        WHEN UPPER(city) LIKE ? THEN 5
                        ELSE 6
                    END,
                    CASE 
                        WHEN country_code = 'IN' THEN 1
                        ELSE 2
                    END,
                    name
                LIMIT ?
            """
            params = (
                search_pattern, search_pattern, search_pattern, search_pattern, search_term_upper,
                search_term_upper,
                f"{search_term_upper}%",
                f"%{search_term_upper}%",
                f"%{search_term_upper}%",
                limit
            )
        
        cursor.execute(sql_query, params)
    else:
        # When no search term, prioritize Indian airports
        popular_indian = get_popular_indian_airports()
        indian_codes = [airport[0] for airport in popular_indian]
        
        # Build SQL query safely - handle empty indian_codes
        if indian_codes:
            in_clause = ','.join(['?' for _ in indian_codes])
            sql_query = f"""
                SELECT code, name, city, country, country_code
                FROM airports
                ORDER BY 
                    CASE 
                        WHEN code IN ({in_clause}) THEN 1
                        WHEN country_code = 'IN' THEN 2
                        ELSE 3
                    END,
                    name
                LIMIT ?
            """
            params = (*indian_codes, limit)
        else:
            # Fallback if no Indian codes available
            sql_query = """
                SELECT code, name, city, country, country_code
                FROM airports
                ORDER BY 
                    CASE 
                        WHEN country_code = 'IN' THEN 1
                        ELSE 2
                    END,
                    name
                LIMIT ?
            """
            params = (limit,)
        
        cursor.execute(sql_query, params)
    
    rows = cursor.fetchall()
    airports = [dict(row) for row in rows]
    
    conn.close()
    return airports


def get_airport_by_code(code: str) -> Optional[Dict]:
    """Get a specific airport by IATA code"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT code, name, city, country, country_code, latitude, longitude, timezone
        FROM airports
        WHERE code = ?
    """, (code.upper(),))
    
    row = cursor.fetchone()
    airport = dict(row) if row else None
    
    conn.close()
    return airport


def delete_unpopular_airports():
    """Delete ALL airports that are NOT tourist destinations - keep only popular international and Indian airports"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get ALL popular airport codes to keep (international + Indian)
    popular_international = get_popular_international_airports()
    popular_indian = get_popular_indian_airports()
    
    # Collect all codes to keep
    popular_codes = set()
    for airport in popular_international:
        popular_codes.add(airport[0])  # code is first element
    for airport in popular_indian:
        popular_codes.add(airport[0])  # code is first element
    
    print(f"🔍 [AIRPORT-DB] Found {len(popular_codes)} popular tourist destination airports to keep")
    print(f"   International: {len(popular_international)}, Indian: {len(popular_indian)}")
    
    # Get count before deletion
    cursor.execute("SELECT COUNT(*) FROM airports")
    total_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'US'")
    usa_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'IN'")
    india_before = cursor.fetchone()[0]
    
    # Delete ALL airports that are NOT in the popular list
    if popular_codes:
        placeholders = ','.join(['?' for _ in popular_codes])
        cursor.execute(f"""
            DELETE FROM airports 
            WHERE code NOT IN ({placeholders})
        """, list(popular_codes))
        deleted_count = cursor.rowcount
    else:
        deleted_count = 0
        print("⚠️ [AIRPORT-DB] No popular airports found, skipping deletion")
    
    conn.commit()
    
    # Get counts after deletion
    cursor.execute("SELECT COUNT(*) FROM airports")
    total_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'US'")
    usa_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM airports WHERE country_code = 'IN'")
    india_after = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ [AIRPORT-DB] Deleted {deleted_count} non-tourist airports")
    print(f"📊 [AIRPORT-DB] Total airports: {total_before} → {total_after}")
    print(f"📊 [AIRPORT-DB] USA airports: {usa_before} → {usa_after}")
    print(f"📊 [AIRPORT-DB] Indian airports: {india_before} → {india_after}")
    
    return deleted_count


def add_airport_from_csv(csv_path: str):
    """Add airports from a CSV file"""
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        airports = []
        for row in reader:
            airports.append((
                row.get('code', '').upper(),
                row.get('name', ''),
                row.get('city', ''),
                row.get('country', ''),
                row.get('country_code', ''),
                float(row.get('latitude', 0)) if row.get('latitude') else None,
                float(row.get('longitude', 0)) if row.get('longitude') else None,
                row.get('timezone', '')
            ))
        
        cursor.executemany("""
            INSERT OR REPLACE INTO airports (code, name, city, country, country_code, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, airports)
    
    conn.commit()
    conn.close()
    print(f"✅ [AIRPORT-DB] Added airports from {csv_path}")

