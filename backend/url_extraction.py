# ================================================================
# URL LOCATION & CATEGORY EXTRACTION SYSTEM
# ================================================================
#
# Features:
#   1. Extract City
#   2. Extract State / Union Territory
#   3. Extract Country
#   4. Extract Region
#   5. Extract URL Location
#   6. Extract Category
#   7. Supports all Indian States and Union Territories
#   8. Supports multi-word Indian cities
#   9. Supports Daman & Diu
#  10. Supports common Indian city aliases
#  11. Handles Tripadvisor URLs
#  12. Handles Zomato URLs
#  13. Handles Markdown-style URLs
#  14. Handles locked CSV files
#
# ================================================================

import re
import html
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote, urlparse

import pandas as pd


# ================================================================
# PATH CONFIGURATION
# ================================================================

BASE_DIR = Path(__file__).resolve().parent

RAW_FOLDER = BASE_DIR / "data" / "raw"
OUTPUT_FOLDER = BASE_DIR / "data" / "processed"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ================================================================
# INDIAN STATES
# ================================================================

INDIAN_STATES = {
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
}


# ================================================================
# UNION TERRITORIES
# ================================================================

INDIAN_UTS = {
    "andaman and nicobar islands":
        "Andaman and Nicobar Islands",

    "andaman & nicobar islands":
        "Andaman and Nicobar Islands",

    "andaman nicobar islands":
        "Andaman and Nicobar Islands",

    "chandigarh":
        "Chandigarh",

    "dadra and nagar haveli and daman and diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "dadra nagar haveli daman diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "dadra and nagar haveli":
        "Dadra and Nagar Haveli and Daman and Diu",

    "daman and diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "daman & diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "daman diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "delhi":
        "Delhi",

    "national capital territory of delhi":
        "Delhi",

    "nct of delhi":
        "Delhi",

    "jammu and kashmir":
        "Jammu and Kashmir",

    "jammu & kashmir":
        "Jammu and Kashmir",

    "jammu kashmir":
        "Jammu and Kashmir",

    "ladakh":
        "Ladakh",

    "lakshadweep":
        "Lakshadweep",

    "puducherry":
        "Puducherry",

    "pondicherry":
        "Puducherry",
}


# ================================================================
# COMBINED STATE / UT DICTIONARY
# ================================================================

ALL_INDIAN_STATES = {}

ALL_INDIAN_STATES.update(INDIAN_STATES)
ALL_INDIAN_STATES.update(INDIAN_UTS)


# ================================================================
# REGION MAPPING
# ================================================================

REGION_MAP = {

    # ------------------------------------------------------------
    # NORTH
    # ------------------------------------------------------------

    "Delhi": "North",
    "Haryana": "North",
    "Himachal Pradesh": "North",
    "Punjab": "North",
    "Rajasthan": "North",
    "Uttarakhand": "North",
    "Jammu and Kashmir": "North",
    "Ladakh": "North",
    "Chandigarh": "North",

    # ------------------------------------------------------------
    # SOUTH
    # ------------------------------------------------------------

    "Andhra Pradesh": "South",
    "Karnataka": "South",
    "Kerala": "South",
    "Tamil Nadu": "South",
    "Telangana": "South",
    "Puducherry": "South",
    "Andaman and Nicobar Islands": "South",
    "Lakshadweep": "South",

    # ------------------------------------------------------------
    # WEST
    # ------------------------------------------------------------

    "Goa": "West",
    "Gujarat": "West",
    "Maharashtra": "West",
    "Dadra and Nagar Haveli and Daman and Diu": "West",

    # ------------------------------------------------------------
    # EAST
    # ------------------------------------------------------------

    "Bihar": "East",
    "Jharkhand": "East",
    "Odisha": "East",
    "West Bengal": "East",

    # ------------------------------------------------------------
    # CENTRAL
    # ------------------------------------------------------------

    "Chhattisgarh": "Central",
    "Madhya Pradesh": "Central",

    # ------------------------------------------------------------
    # NORTH EAST
    # ------------------------------------------------------------

    "Arunachal Pradesh": "North East",
    "Assam": "North East",
    "Manipur": "North East",
    "Meghalaya": "North East",
    "Mizoram": "North East",
    "Nagaland": "North East",
    "Sikkim": "North East",
    "Tripura": "North East",
}


# ================================================================
# CITY ALIASES
# ================================================================
#
# IMPORTANT:
# Longer / multi-word cities are intentionally included.
# The extraction function checks these BEFORE generic matching.
#
# ================================================================

CITY_ALIASES = {

    # ============================================================
    # DELHI / NCR
    # ============================================================

    "new delhi": "New Delhi",
    "new_delhi": "New Delhi",

    "greater noida": "Greater Noida",
    "greater_noida": "Greater Noida",

    "navi mumbai": "Navi Mumbai",
    "navi_mumbai": "Navi Mumbai",

    "gurugram": "Gurugram",
    "gurgaon": "Gurugram",

    "faridabad": "Faridabad",
    "ghaziabad": "Ghaziabad",
    "noida": "Noida",

    # ============================================================
    # MAHARASHTRA
    # ============================================================

    "mumbai": "Mumbai",
    "bombay": "Mumbai",

    "navi mumbai": "Navi Mumbai",

    "thane": "Thane",
    "kalyan": "Kalyan",
    "pune": "Pune",
    "nagpur": "Nagpur",
    "nashik": "Nashik",
    "nasik": "Nashik",
    "aurangabad": "Aurangabad",
    "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar",
    "solapur": "Solapur",
    "kolhapur": "Kolhapur",
    "satara": "Satara",
    "ratnagiri": "Ratnagiri",
    "alibag": "Alibag",
    "lonavala": "Lonavala",
    "mahabaleshwar": "Mahabaleshwar",

    # ============================================================
    # KARNATAKA
    # ============================================================

    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",

    "mysuru": "Mysuru",
    "mysore": "Mysuru",

    "mangalore": "Mangaluru",
    "mangaluru": "Mangaluru",

    "hubli": "Hubballi",
    "hubballi": "Hubballi",

    "belgaum": "Belagavi",
    "belagavi": "Belagavi",

    "coorg": "Coorg",
    "madikeri": "Madikeri",

    "hampi": "Hampi",

    # ============================================================
    # TAMIL NADU
    # ============================================================

    "chennai": "Chennai",
    "madras": "Chennai",

    "coimbatore": "Coimbatore",
    "madurai": "Madurai",
    "salem": "Salem",
    "tiruchirappalli": "Tiruchirappalli",
    "trichy": "Tiruchirappalli",
    "tirunelveli": "Tirunelveli",
    "thoothukudi": "Thoothukudi",
    "tuticorin": "Thoothukudi",

    "rameswaram": "Rameswaram",
    "ooty": "Ooty",
    "udagamandalam": "Ooty",
    "kodaikanal": "Kodaikanal",
    "kanyakumari": "Kanyakumari",
    "mahabalipuram": "Mahabalipuram",
    "mamallapuram": "Mahabalipuram",

    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",

    "thanjavur": "Thanjavur",
    "tanjore": "Thanjavur",

    "vellore": "Vellore",
    "erode": "Erode",

    # ============================================================
    # KERALA
    # ============================================================

    "kochi": "Kochi",
    "cochin": "Kochi",

    "thiruvananthapuram": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram",

    "kozhikode": "Kozhikode",
    "calicut": "Kozhikode",

    "thrissur": "Thrissur",
    "trichur": "Thrissur",

    "kollam": "Kollam",
    "alleppey": "Alappuzha",
    "alappuzha": "Alappuzha",

    "kottayam": "Kottayam",
    "munnar": "Munnar",
    "varkala": "Varkala",
    "kovalam": "Kovalam",
    "thekkady": "Thekkady",

    # ============================================================
    # TELANGANA
    # ============================================================

    "hyderabad": "Hyderabad",
    "secunderabad": "Secunderabad",
    "warangal": "Warangal",
    "nizamabad": "Nizamabad",
    "karimnagar": "Karimnagar",

    # ============================================================
    # ANDHRA PRADESH
    # ============================================================

    "visakhapatnam": "Visakhapatnam",
    "vizag": "Visakhapatnam",

    "vijayawada": "Vijayawada",
    "tirupati": "Tirupati",
    "guntur": "Guntur",
    "nellore": "Nellore",
    "kurnool": "Kurnool",
    "rajahmundry": "Rajahmundry",
    "kakinada": "Kakinada",
    "amaravati": "Amaravati",

    # ============================================================
    # GUJARAT
    # ============================================================

    "ahmedabad": "Ahmedabad",
    "surat": "Surat",
    "vadodara": "Vadodara",
    "baroda": "Vadodara",

    "rajkot": "Rajkot",
    "bhavnagar": "Bhavnagar",
    "jamnagar": "Jamnagar",
    "gandhinagar": "Gandhinagar",

    "dwarka": "Dwarka",
    "somnath": "Somnath",
    "porbandar": "Porbandar",
    "bhuj": "Bhuj",

    # ============================================================
    # RAJASTHAN
    # ============================================================

    "jaipur": "Jaipur",
    "jodhpur": "Jodhpur",
    "udaipur": "Udaipur",
    "kota": "Kota",
    "ajmer": "Ajmer",
    "bikaner": "Bikaner",
    "pushkar": "Pushkar",
    "mount abu": "Mount Abu",
    "mount_abu": "Mount Abu",

    # ============================================================
    # UTTAR PRADESH
    # ============================================================

    "lucknow": "Lucknow",
    "kanpur": "Kanpur",
    "agra": "Agra",
    "varanasi": "Varanasi",
    "allahabad": "Prayagraj",
    "prayagraj": "Prayagraj",
    "mathura": "Mathura",
    "vrindavan": "Vrindavan",
    "ayodhya": "Ayodhya",
    "meerut": "Meerut",
    "bareilly": "Bareilly",
    "aligarh": "Aligarh",
    "gorakhpur": "Gorakhpur",
    "jhansi": "Jhansi",
    "fatehpur sikri": "Fatehpur Sikri",
    "fatehpur_sikri": "Fatehpur Sikri",

    # ============================================================
    # UTTARAKHAND
    # ============================================================

    "dehradun": "Dehradun",
    "haridwar": "Haridwar",
    "rishikesh": "Rishikesh",
    "mussoorie": "Mussoorie",
    "nainital": "Nainital",
    "almora": "Almora",
    "ranikhet": "Ranikhet",
    "jim corbett": "Jim Corbett",
    "jim_corbett": "Jim Corbett",

    # ============================================================
    # HIMACHAL PRADESH
    # ============================================================

    "shimla": "Shimla",
    "manali": "Manali",
    "dharamshala": "Dharamshala",
    "dharamsala": "Dharamshala",
    "mcleod ganj": "McLeod Ganj",
    "mcleod_ganj": "McLeod Ganj",
    "kullu": "Kullu",
    "dalhousie": "Dalhousie",
    "kasol": "Kasol",
    "spiti": "Spiti",

    # ============================================================
    # PUNJAB
    # ============================================================

    "amritsar": "Amritsar",
    "ludhiana": "Ludhiana",
    "jalandhar": "Jalandhar",
    "patiala": "Patiala",
    "bathinda": "Bathinda",

    # ============================================================
    # JAMMU & KASHMIR
    # ============================================================

    "srinagar": "Srinagar",
    "jammu": "Jammu",
    "gulmarg": "Gulmarg",
    "pahalgam": "Pahalgam",
    "sonamarg": "Sonamarg",
    "kashmir": "Kashmir",

    # ============================================================
    # LADAKH
    # ============================================================

    "leh": "Leh",
    "kargil": "Kargil",

    # ============================================================
    # WEST BENGAL
    # ============================================================

    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "darjeeling": "Darjeeling",
    "siliguri": "Siliguri",
    "durgapur": "Durgapur",
    "howrah": "Howrah",
    "kalimpong": "Kalimpong",

    # ============================================================
    # ODISHA
    # ============================================================

    "bhubaneswar": "Bhubaneswar",
    "cuttack": "Cuttack",
    "puri": "Puri",
    "konark": "Konark",
    "rourkela": "Rourkela",

    # ============================================================
    # BIHAR
    # ============================================================

    "patna": "Patna",
    "gaya": "Gaya",
    "bodh gaya": "Bodh Gaya",
    "bodh_gaya": "Bodh Gaya",
    "muzaffarpur": "Muzaffarpur",

    # ============================================================
    # JHARKHAND
    # ============================================================

    "ranchi": "Ranchi",
    "jamshedpur": "Jamshedpur",
    "dhanbad": "Dhanbad",
    "deoghar": "Deoghar",

    # ============================================================
    # MADHYA PRADESH
    # ============================================================

    "bhopal": "Bhopal",
    "indore": "Indore",
    "gwalior": "Gwalior",
    "jabalpur": "Jabalpur",
    "ujjain": "Ujjain",
    "khajuraho": "Khajuraho",
    "sanchi": "Sanchi",
    "mandu": "Mandu",

    # ============================================================
    # CHHATTISGARH
    # ============================================================

    "raipur": "Raipur",
    "bilaspur": "Bilaspur",
    "durg": "Durg",
    "bhilai": "Bhilai",

    # ============================================================
    # ASSAM
    # ============================================================

    "guwahati": "Guwahati",
    "dibrugarh": "Dibrugarh",
    "jorhat": "Jorhat",
    "silchar": "Silchar",
    "kaziranga": "Kaziranga",

    # ============================================================
    # NORTH EAST
    # ============================================================

    "shillong": "Shillong",
    "cherrapunji": "Cherrapunji",
    "gangtok": "Gangtok",
    "imphal": "Imphal",
    "aizawl": "Aizawl",
    "kohima": "Kohima",
    "agartala": "Agartala",
    "itanagar": "Itanagar",

    # ============================================================
    # GOA
    # ============================================================

    "panaji": "Panaji",
    "panjim": "Panaji",

    "margao": "Margao",
    "madgaon": "Margao",

    "vasco da gama": "Vasco da Gama",
    "vasco_da_gama": "Vasco da Gama",

    "calangute": "Calangute",
    "baga": "Baga",
    "anjuna": "Anjuna",
    "candolim": "Candolim",
    "palolem": "Palolem",

    # ============================================================
    # DAMAN / DNH
    # ============================================================

    "daman": "Daman",
    "diu": "Diu",
    "silvassa": "Silvassa",

    # ============================================================
    # OTHER UT
    # ============================================================

    "port blair": "Port Blair",
    "port_blair": "Port Blair",

    "kavaratti": "Kavaratti",

    # ============================================================
    # COMMON TOURIST LOCATIONS
    # ============================================================

    "rameswaram": "Rameswaram",
    "munnar": "Munnar",
    "ooty": "Ooty",
    "manali": "Manali",
    "munnar": "Munnar",
    "darjeeling": "Darjeeling",
    "puri": "Puri",
    "varanasi": "Varanasi",
    "pushkar": "Pushkar",
    "rishikesh": "Rishikesh",
    "haridwar": "Haridwar",
}


# ================================================================
# SORT CITY ALIASES
# ================================================================
#
# Longest names first.
# This is critical for:
#
#   New Delhi
#   Navi Mumbai
#   Greater Noida
#   Vasco da Gama
#
# ================================================================

SORTED_CITY_ALIASES = sorted(
    CITY_ALIASES.items(),
    key=lambda x: len(x[0]),
    reverse=True
)


# ================================================================
# GENERIC URL CATEGORY MAP
# ================================================================

CATEGORY_PATTERNS = [

    (
        "Restaurant",
        [
            "restaurant_review",
            "restaurantsnear",
            "restaurants",
            "restaurant",
            "dining",
            "food",
            "cafe",
            "cafes",
        ]
    ),

    (
        "Hotel",
        [
            "hotels",
            "hotel",
            "accommodation",
            "resort",
            "resorts",
        ]
    ),

    (
        "Attraction",
        [
            "attraction_review",
            "attractions",
            "activities",
            "things_to_do",
            "thingstodo",
        ]
    ),

    (
        "Tourism",
        [
            "tourism",
            "vacations",
            "travel",
        ]
    ),
]


# ================================================================
# NORMALIZE URL
# ================================================================

def normalize_url(value):
    """
    Convert URL value into a clean plain URL.

    Handles:
        [https://example.com](https://example.com)
        HTML entities
        encoded URLs
        whitespace
    """

    if pd.isna(value):
        return ""

    url = str(value).strip()

    if not url:
        return ""

    # HTML entities
    url = html.unescape(url)

    # Markdown link:
    # [text](url)
    markdown_match = re.search(
        r"\]\((https?://[^)]+)\)",
        url,
        flags=re.IGNORECASE
    )

    if markdown_match:
        url = markdown_match.group(1)

    else:
        # If URL appears somewhere inside text
        plain_match = re.search(
            r"https?://[^\s)\]]+",
            url,
            flags=re.IGNORECASE
        )

        if plain_match:
            url = plain_match.group(0)

    # Decode URL
    url = unquote(url)

    # Remove trailing punctuation
    url = url.strip(" <>\"'")

    url = url.rstrip(".,;")

    return url


# ================================================================
# NORMALIZE LOCATION TEXT
# ================================================================

def normalize_location_text(text):
    """
    Normalize URL slug/location text for matching.
    """

    if not text:
        return ""

    text = unquote(str(text))

    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = text.replace("%20", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


# ================================================================
# GET URL PATH
# ================================================================

def get_url_path(url):
    """
    Return decoded URL path.
    """

    try:
        parsed = urlparse(url)

        path = parsed.path

        path = unquote(path)

        return path

    except Exception:
        return url


# ================================================================
# GET URL SLUG TEXT
# ================================================================

def get_search_text(url):
    """
    Creates a searchable version of the URL.
    """

    path = get_url_path(url)

    text = normalize_location_text(path)

    return text


# ================================================================
# STATE EXTRACTION
# ================================================================

def extract_state(url):
    """
    Extract Indian state / UT from URL.

    Longer states are checked first so that:
        Daman and Diu
        Jammu and Kashmir
        Dadra and Nagar Haveli...
    are correctly detected.
    """

    search_text = get_search_text(url)

    if not search_text:
        return "Unknown"

    # Sort longest state names first
    sorted_states = sorted(
        ALL_INDIAN_STATES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for state_key, state_name in sorted_states:

        pattern = r"(?<![a-z])" + re.escape(state_key) + r"(?![a-z])"

        if re.search(pattern, search_text):
            return state_name

    return "Unknown"


# ================================================================
# COUNTRY EXTRACTION
# ================================================================

def extract_country(state):
    """
    If an Indian state/UT is detected,
    country is India.
    """

    if state != "Unknown":
        return "India"

    return "Unknown"


# ================================================================
# REGION EXTRACTION
# ================================================================

def extract_region(state):
    """
    Get Indian geographical region.
    """

    return REGION_MAP.get(state, "Unknown")


# ================================================================
# FIND CITY BY KNOWN CITY LIST
# ================================================================

def find_known_city(search_text, state="Unknown"):
    """
    Find city from known city aliases.

    Multi-word cities are checked first.
    """

    if not search_text:
        return "Unknown"

    # ------------------------------------------------------------
    # State-specific city filtering
    # ------------------------------------------------------------

    state_city_rules = {

        "Delhi": {
            "new delhi",
            "new_delhi",
            "delhi",
        },

        "Maharashtra": {
            "mumbai",
            "navi mumbai",
            "thane",
            "kalyan",
            "pune",
            "nagpur",
            "nashik",
            "nasik",
            "aurangabad",
            "chhatrapati sambhajinagar",
            "solapur",
            "kolhapur",
            "satara",
            "ratnagiri",
            "alibag",
            "lonavala",
            "mahabaleshwar",
        },

        "Karnataka": {
            "bengaluru",
            "bangalore",
            "mysuru",
            "mysore",
            "mangalore",
            "mangaluru",
            "hubli",
            "hubballi",
            "belgaum",
            "belagavi",
            "coorg",
            "madikeri",
            "hampi",
        },

        "Tamil Nadu": {
            "chennai",
            "madras",
            "coimbatore",
            "madurai",
            "salem",
            "tiruchirappalli",
            "trichy",
            "tirunelveli",
            "thoothukudi",
            "tuticorin",
            "rameswaram",
            "ooty",
            "udagamandalam",
            "kodaikanal",
            "kanyakumari",
            "mahabalipuram",
            "mamallapuram",
            "thanjavur",
            "tanjore",
            "vellore",
            "erode",
        },

        "Kerala": {
            "kochi",
            "cochin",
            "thiruvananthapuram",
            "trivandrum",
            "kozhikode",
            "calicut",
            "thrissur",
            "trichur",
            "kollam",
            "alleppey",
            "alappuzha",
            "kottayam",
            "munnar",
            "varkala",
            "kovalam",
            "thekkady",
        },

        "Telangana": {
            "hyderabad",
            "secunderabad",
            "warangal",
            "nizamabad",
            "karimnagar",
        },

        "Andhra Pradesh": {
            "visakhapatnam",
            "vizag",
            "vijayawada",
            "tirupati",
            "guntur",
            "nellore",
            "kurnool",
            "rajahmundry",
            "kakinada",
            "amaravati",
        },

        "Gujarat": {
            "ahmedabad",
            "surat",
            "vadodara",
            "baroda",
            "rajkot",
            "bhavnagar",
            "jamnagar",
            "gandhinagar",
            "dwarka",
            "somnath",
            "porbandar",
            "bhuj",
        },

        "Rajasthan": {
            "jaipur",
            "jodhpur",
            "udaipur",
            "kota",
            "ajmer",
            "bikaner",
            "pushkar",
            "mount abu",
            "mount_abu",
        },

        "Uttar Pradesh": {
            "lucknow",
            "kanpur",
            "agra",
            "varanasi",
            "allahabad",
            "prayagraj",
            "mathura",
            "vrindavan",
            "ayodhya",
            "meerut",
            "bareilly",
            "aligarh",
            "gorakhpur",
            "jhansi",
            "fatehpur sikri",
            "fatehpur_sikri",
            "noida",
            "greater noida",
            "greater_noida",
        },

        "Uttarakhand": {
            "dehradun",
            "haridwar",
            "rishikesh",
            "mussoorie",
            "nainital",
            "almora",
            "ranikhet",
            "jim corbett",
            "jim_corbett",
        },

        "Himachal Pradesh": {
            "shimla",
            "manali",
            "dharamshala",
            "dharamsala",
            "mcleod ganj",
            "mcleod_ganj",
            "kullu",
            "dalhousie",
            "kasol",
            "spiti",
        },

        "Punjab": {
            "amritsar",
            "ludhiana",
            "jalandhar",
            "patiala",
            "bathinda",
        },

        "Jammu and Kashmir": {
            "srinagar",
            "jammu",
            "gulmarg",
            "pahalgam",
            "sonamarg",
            "kashmir",
        },

        "Ladakh": {
            "leh",
            "kargil",
        },

        "West Bengal": {
            "kolkata",
            "calcutta",
            "darjeeling",
            "siliguri",
            "durgapur",
            "howrah",
            "kalimpong",
        },

        "Odisha": {
            "bhubaneswar",
            "cuttack",
            "puri",
            "konark",
            "rourkela",
        },

        "Bihar": {
            "patna",
            "gaya",
            "bodh gaya",
            "bodh_gaya",
            "muzaffarpur",
        },

        "Jharkhand": {
            "ranchi",
            "jamshedpur",
            "dhanbad",
            "deoghar",
        },

        "Madhya Pradesh": {
            "bhopal",
            "indore",
            "gwalior",
            "jabalpur",
            "ujjain",
            "khajuraho",
            "sanchi",
            "mandu",
        },

        "Chhattisgarh": {
            "raipur",
            "bilaspur",
            "durg",
            "bhilai",
        },

        "Assam": {
            "guwahati",
            "dibrugarh",
            "jorhat",
            "silchar",
            "kaziranga",
        },

        "Goa": {
            "panaji",
            "panjim",
            "margao",
            "madgaon",
            "vasco da gama",
            "vasco_da_gama",
            "calangute",
            "baga",
            "anjuna",
            "candolim",
            "palolem",
        },

        "Dadra and Nagar Haveli and Daman and Diu": {
            "daman",
            "diu",
            "silvassa",
        },

        "Puducherry": {
            "puducherry",
            "pondicherry",
        },

        "Andaman and Nicobar Islands": {
            "port blair",
            "port_blair",
        },

        "Lakshadweep": {
            "kavaratti",
        },

        "Sikkim": {
            "gangtok",
        },

        "Meghalaya": {
            "shillong",
            "cherrapunji",
        },

        "Manipur": {
            "imphal",
        },

        "Mizoram": {
            "aizawl",
        },

        "Nagaland": {
            "kohima",
        },

        "Tripura": {
            "agartala",
        },

        "Arunachal Pradesh": {
            "itanagar",
        },
    }

    allowed = state_city_rules.get(state)

    # ------------------------------------------------------------
    # If state is known, first check its cities
    # ------------------------------------------------------------

    if allowed:

        sorted_allowed = sorted(
            allowed,
            key=len,
            reverse=True
        )

        for city_key in sorted_allowed:

            normalized_city = normalize_location_text(city_key)

            pattern = (
                r"(?<![a-z])"
                + re.escape(normalized_city)
                + r"(?![a-z])"
            )

            if re.search(pattern, search_text):
                return CITY_ALIASES.get(
                    city_key,
                    city_key.title()
                )

    # ------------------------------------------------------------
    # Fallback: search all cities
    # ------------------------------------------------------------

    for city_key, city_name in SORTED_CITY_ALIASES:

        normalized_city = normalize_location_text(city_key)

        pattern = (
            r"(?<![a-z])"
            + re.escape(normalized_city)
            + r"(?![a-z])"
        )

        if re.search(pattern, search_text):
            return city_name

    return "Unknown"


# ================================================================
# GENERIC CITY EXTRACTION FROM TRIPADVISOR URL
# ================================================================

def extract_city_from_tripadvisor_slug(url, state):
    """
    Fallback parser for Tripadvisor URLs.

    Examples:

        Kalyan_Thane_District_Maharashtra
        Tirupati_Chittoor_District_Andhra_Pradesh
        Virudhunagar_Virudhunagar_District_Tamil_Nadu
        Daman_Daman_and_Diu

    """

    path = get_url_path(url)

    if not path:
        return "Unknown"

    # ------------------------------------------------------------
    # Remove extension
    # ------------------------------------------------------------

    path = re.sub(
        r"\.html?$",
        "",
        path,
        flags=re.IGNORECASE
    )

    # ------------------------------------------------------------
    # Get last path section
    # ------------------------------------------------------------

    slug = path.split("/")[-1]

    if not slug:
        return "Unknown"

    # ------------------------------------------------------------
    # Tripadvisor removes some information into:
    #
    #   -Reviews-City...
    #   -City...
    #
    # ------------------------------------------------------------

    # Remove known Tripadvisor prefixes
    slug = re.sub(
        r"^(Reviews-|Activities-|Hotels-|Restaurants-|Vacations-)",
        "",
        slug,
        flags=re.IGNORECASE
    )

    # ------------------------------------------------------------
    # Convert underscores to spaces
    # ------------------------------------------------------------

    clean_slug = normalize_location_text(slug)

    if not clean_slug:
        return "Unknown"

    # ------------------------------------------------------------
    # If state known, attempt to isolate text before state.
    # ------------------------------------------------------------

    if state != "Unknown":

        state_key = state.lower()

        # Special state aliases
        state_variants = [
            state_key,
            state_key.replace(" ", "_"),
        ]

        if state == "Delhi":
            state_variants.extend([
                "national capital territory of delhi",
                "national_capital_territory_of_delhi",
            ])

        if state == "Jammu and Kashmir":
            state_variants.extend([
                "jammu and kashmir",
                "jammu_and_kashmir",
            ])

        if state == "Dadra and Nagar Haveli and Daman and Diu":
            state_variants.extend([
                "daman and diu",
                "daman_and_diu",
                "dadra and nagar haveli and daman and diu",
                "dadra_and_nagar_haveli_and_daman_and_diu",
            ])

        # Find the state in original slug
        original_slug = slug.lower()

        state_position = -1
        matched_state_variant = None

        for variant in sorted(
            state_variants,
            key=len,
            reverse=True
        ):

            pos = original_slug.rfind(variant)

            if pos != -1:

                if pos > state_position:
                    state_position = pos
                    matched_state_variant = variant

        if state_position >= 0 and matched_state_variant:

            before_state = original_slug[
                :state_position
            ].strip("_- ")

            before_state = normalize_location_text(
                before_state
            )

        else:
            before_state = clean_slug

    else:
        before_state = clean_slug

    # ------------------------------------------------------------
    # Remove common Tripadvisor suffixes
    # ------------------------------------------------------------

    before_state = re.sub(
        r"\b(?:district|state|india)\b",
        " ",
        before_state,
        flags=re.IGNORECASE
    )

    before_state = re.sub(
        r"\bnational capital territory\b",
        " ",
        before_state,
        flags=re.IGNORECASE
    )

    before_state = re.sub(
        r"\b(?:north|south|east|west|central)\b",
        " ",
        before_state,
        flags=re.IGNORECASE
    )

    before_state = re.sub(
        r"\b(?:goa|kashmir)\b",
        " ",
        before_state,
        flags=re.IGNORECASE
    )

    before_state = re.sub(
        r"\s+",
        " ",
        before_state
    ).strip()

    # ------------------------------------------------------------
    # Remove district information
    # ------------------------------------------------------------

    before_state = re.sub(
        r"\b[a-z ]*district\b",
        " ",
        before_state,
        flags=re.IGNORECASE
    )

    before_state = re.sub(
        r"\s+",
        " ",
        before_state
    ).strip()

    # ------------------------------------------------------------
    # Try known city again on reduced text
    # ------------------------------------------------------------

    city = find_known_city(
        before_state,
        state
    )

    if city != "Unknown":
        return city

    # ------------------------------------------------------------
    # Split slug
    # ------------------------------------------------------------

    parts = [
        x.strip()
        for x in before_state.split()
        if x.strip()
    ]

    if not parts:
        return "Unknown"

    # ------------------------------------------------------------
    # Remove common location descriptors
    # ------------------------------------------------------------

    stop_words = {
        "district",
        "national",
        "capital",
        "territory",
        "north",
        "south",
        "east",
        "west",
        "central",
    }

    parts = [
        p for p in parts
        if p.lower() not in stop_words
    ]

    if not parts:
        return "Unknown"

    # ------------------------------------------------------------
    # First meaningful part is usually city
    # ------------------------------------------------------------

    candidate = parts[0]

    candidate = candidate.strip()

    if len(candidate) < 2:
        return "Unknown"

    return candidate.title()


# ================================================================
# CITY EXTRACTION
# ================================================================

def extract_city(url, state):
    """
    Main city extraction function.
    """

    search_text = get_search_text(url)

    if not search_text:
        return "Unknown"

    # ------------------------------------------------------------
    # IMPORTANT:
    # Known city extraction comes FIRST.
    # This prevents:
    #
    # Anjuna_Bardez_North_Goa_District_Goa
    #
    # from becoming:
    #
    # City = Goa
    #
    # ------------------------------------------------------------

    city = find_known_city(
        search_text,
        state
    )

    if city != "Unknown":
        return city

    # ------------------------------------------------------------
    # Tripadvisor fallback
    # ------------------------------------------------------------

    if "tripadvisor" in search_text:

        city = extract_city_from_tripadvisor_slug(
            url,
            state
        )

        if city != "Unknown":
            return city

    return "Unknown"


# ================================================================
# URL LOCATION
# ================================================================

def extract_url_location(city, state):
    """
    Create URL_Location value.
    """

    if city != "Unknown":
        return city

    return "Unknown"


# ================================================================
# CATEGORY EXTRACTION
# ================================================================

def extract_category(url):
    """
    Extract category from URL.
    """

    if not url:
        return "Unknown"

    text = get_search_text(url)

    if not text:
        return "Unknown"

    # ------------------------------------------------------------
    # More specific patterns first
    # ------------------------------------------------------------

    # Restaurants
    restaurant_patterns = [
        "restaurant_review",
        "restaurantsnear",
        "restaurants",
        "restaurant",
    ]

    for pattern in restaurant_patterns:

        if pattern in text:
            return "Restaurant"

    # Hotels
    hotel_patterns = [
        "hotels",
        "hotel",
        "resorts",
        "resort",
    ]

    for pattern in hotel_patterns:

        if pattern in text:
            return "Hotel"

    # Attractions
    attraction_patterns = [
        "attraction_review",
        "attractions",
        "activities",
        "things_to_do",
        "thingstodo",
    ]

    for pattern in attraction_patterns:

        if pattern in text:
            return "Attraction"

    # Tourism
    tourism_patterns = [
        "tourism",
        "vacations",
        "vacation",
        "travel",
    ]

    for pattern in tourism_patterns:

        if pattern in text:
            return "Tourism"

    # Cafes
    if "cafe" in text or "cafes" in text:
        return "Restaurant"

    return "Unknown"


# ================================================================
# PROCESS ONE URL
# ================================================================

def extract_location_data(url):
    """
    Extract all location/category fields from one URL.
    """

    clean_url = normalize_url(url)

    if not clean_url:
        return {
            "City": "Unknown",
            "State": "Unknown",
            "Country": "Unknown",
            "Region": "Unknown",
            "URL_Location": "Unknown",
            "Category": "Unknown",
        }

    # ------------------------------------------------------------
    # State FIRST
    # ------------------------------------------------------------

    state = extract_state(clean_url)

    # ------------------------------------------------------------
    # Country
    # ------------------------------------------------------------

    country = extract_country(state)

    # ------------------------------------------------------------
    # Region
    # ------------------------------------------------------------

    region = extract_region(state)

    # ------------------------------------------------------------
    # City
    # ------------------------------------------------------------

    city = extract_city(
        clean_url,
        state
    )

    # ------------------------------------------------------------
    # URL location
    # ------------------------------------------------------------

    url_location = extract_url_location(
        city,
        state
    )

    # ------------------------------------------------------------
    # Category
    # ------------------------------------------------------------

    category = extract_category(
        clean_url
    )

    return {
        "City": city,
        "State": state,
        "Country": country,
        "Region": region,
        "URL_Location": url_location,
        "Category": category,
    }


# ================================================================
# DETECT URL COLUMN
# ================================================================

def find_url_column(df):
    """
    Automatically find ranking URL column.
    """

    possible_columns = [
        "Ranking URL",
        "Ranking_URL",
        "URL",
        "url",
        "Url",
        "RankingURL",
        "ranking_url",
    ]

    # Exact matches first
    for column in possible_columns:

        if column in df.columns:
            return column

    # Fuzzy match
    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
            .replace("_", " ")
        )

        if "ranking" in normalized and "url" in normalized:
            return column

        if normalized == "url":
            return column

    return None


# ================================================================
# READ CSV SAFELY
# ================================================================

def read_csv_safely(file_path):
    """
    Read CSV with multiple encoding fallbacks.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
    ]

    last_error = None

    for encoding in encodings:

        try:

            df = pd.read_csv(
                file_path,
                encoding=encoding,
                low_memory=False
            )

            return df

        except Exception as error:

            last_error = error

    raise last_error


# ================================================================
# SAFE CSV SAVE
# ================================================================

def safe_save_csv(df, output_path):
    """
    Save CSV safely.

    If the target file is locked by:
        Excel
        VS Code
        OneDrive
        another process

    the script creates an alternate file instead of crashing.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ------------------------------------------------------------
    # Attempt 1: normal save
    # ------------------------------------------------------------

    try:

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print()
        print("Output saved successfully:")
        print(f"  {output_path}")

        return output_path

    except PermissionError:

        print()
        print("=" * 70)
        print("WARNING: OUTPUT FILE IS LOCKED")
        print("=" * 70)

        print(f"Locked file:")
        print(f"  {output_path}")

        print()
        print(
            "The file may be open in Excel, VS Code, "
            "OneDrive, or another program."
        )

    # ------------------------------------------------------------
    # Attempt 2: _new.csv
    # ------------------------------------------------------------

    new_path = output_path.with_name(
        output_path.stem + "_new.csv"
    )

    try:

        df.to_csv(
            new_path,
            index=False,
            encoding="utf-8-sig"
        )

        print()
        print("Saved using alternate filename:")
        print(f"  {new_path}")

        return new_path

    except PermissionError:
        pass

    # ------------------------------------------------------------
    # Attempt 3: timestamped filename
    # ------------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    timestamp_path = output_path.with_name(
        f"{output_path.stem}_{timestamp}.csv"
    )

    try:

        df.to_csv(
            timestamp_path,
            index=False,
            encoding="utf-8-sig"
        )

        print()
        print("Saved using timestamped filename:")
        print(f"  {timestamp_path}")

        return timestamp_path

    except PermissionError as error:

        print()
        print("=" * 70)
        print("ERROR: COULD NOT SAVE OUTPUT FILE")
        print("=" * 70)

        print(error)

        return None


# ================================================================
# PRINT SAMPLE RESULTS
# ================================================================

def print_sample_results(df):
    """
    Print first 30 enriched rows.
    """

    print()
    print("=" * 70)
    print("SAMPLE RESULTS")
    print("=" * 70)

    columns = [
        "Ranking URL",
        "City",
        "State",
        "Country",
        "Region",
        "URL_Location",
        "Category",
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    if not available:
        print(df.head(30).to_string())
        return

    print(
        df[available]
        .head(30)
        .to_string(index=False)
    )


# ================================================================
# PRINT DISTRIBUTION
# ================================================================

def print_distribution(df):
    """
    Print City, State, Region and Category distributions.
    """

    # ------------------------------------------------------------
    # CITY
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("CITY DISTRIBUTION")
    print("=" * 70)

    if "City" in df.columns:

        print(
            df["City"]
            .value_counts(dropna=False)
            .head(30)
            .to_string()
        )

    # ------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("STATE DISTRIBUTION")
    print("=" * 70)

    if "State" in df.columns:

        print(
            df["State"]
            .value_counts(dropna=False)
            .to_string()
        )

    # ------------------------------------------------------------
    # REGION
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("REGION DISTRIBUTION")
    print("=" * 70)

    if "Region" in df.columns:

        print(
            df["Region"]
            .value_counts(dropna=False)
            .to_string()
        )

    # ------------------------------------------------------------
    # CATEGORY
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("CATEGORY DISTRIBUTION")
    print("=" * 70)

    if "Category" in df.columns:

        print(
            df["Category"]
            .value_counts(dropna=False)
            .to_string()
        )


# ================================================================
# PRINT UNKNOWN COUNTS
# ================================================================

def print_unknown_counts(df):
    """
    Print unknown values and city match rate.
    """

    print()
    print("=" * 70)
    print("UNKNOWN COUNTS")
    print("=" * 70)

    fields = [
        "City",
        "State",
        "Country",
        "Region",
        "Category",
    ]

    for field in fields:

        if field in df.columns:

            unknown_count = (
                df[field]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.lower()
                .eq("unknown")
                .sum()
            )

            print(
                f"{field}: {unknown_count}"
            )

    # ------------------------------------------------------------
    # City match rate
    # ------------------------------------------------------------

    if "City" in df.columns and len(df) > 0:

        city_unknown = (
            df["City"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("unknown")
            .sum()
        )

        city_matched = len(df) - city_unknown

        match_rate = (
            city_matched / len(df)
        ) * 100

        print()
        print(
            f"City Match Rate: {match_rate:.2f}%"
        )


# ================================================================
# PROCESS ONE CSV FILE
# ================================================================

def process_file(file_name):
    """
    Process one CSV file.
    """

    input_path = RAW_FOLDER / file_name

    # Output filename
    output_name = (
        input_path.stem +
        "_enriched.csv"
    )

    output_path = OUTPUT_FOLDER / output_name

    print()
    print("=" * 70)
    print(f"PROCESSING: {file_name}")
    print("=" * 70)

    # ------------------------------------------------------------
    # Read
    # ------------------------------------------------------------

    try:

        df = read_csv_safely(
            input_path
        )

    except Exception as error:

        print()
        print("ERROR: Could not read CSV.")
        print(error)

        return False

    print(
        f"Original Shape: {df.shape}"
    )

    print(
        f"Columns: {list(df.columns)}"
    )

    # ------------------------------------------------------------
    # Detect URL column
    # ------------------------------------------------------------

    url_column = find_url_column(df)

    if url_column is None:

        print()
        print("ERROR: No URL column found.")

        print(
            "Available columns:"
        )

        for column in df.columns:
            print(f"  - {column}")

        return False

    print(
        f"URL Column: {url_column}"
    )

    # ------------------------------------------------------------
    # Extract location
    # ------------------------------------------------------------

    print()
    print(
        "Extracting City / State / Country / Region..."
    )

    location_results = []

    for index, url in enumerate(
        df[url_column]
    ):

        try:

            result = extract_location_data(
                url
            )

        except Exception:

            result = {
                "City": "Unknown",
                "State": "Unknown",
                "Country": "Unknown",
                "Region": "Unknown",
                "URL_Location": "Unknown",
                "Category": "Unknown",
            }

        location_results.append(
            result
        )

    # ------------------------------------------------------------
    # Convert to DataFrame
    # ------------------------------------------------------------

    location_df = pd.DataFrame(
        location_results
    )

    # ------------------------------------------------------------
    # Add enrichment columns
    # ------------------------------------------------------------

    df["City"] = location_df["City"]
    df["State"] = location_df["State"]
    df["Country"] = location_df["Country"]
    df["Region"] = location_df["Region"]
    df["URL_Location"] = location_df[
        "URL_Location"
    ]

    print(
        "Extracting categories..."
    )

    df["Category"] = location_df[
        "Category"
    ]

    # ------------------------------------------------------------
    # Print results
    # ------------------------------------------------------------

    print_sample_results(df)

    print_distribution(df)

    print_unknown_counts(df)

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    saved_path = safe_save_csv(
        df,
        output_path
    )

    if saved_path is None:

        print()
        print(
            f"FAILED TO SAVE: {file_name}"
        )

        return False

    print()
    print(
        f"Final Shape: {df.shape}"
    )

    return True


# ================================================================
# FIND CSV FILES
# ================================================================

def find_csv_files():
    """
    Find all CSV files in raw folder.
    """

    if not RAW_FOLDER.exists():

        print()
        print("ERROR:")
        print(
            f"Raw folder does not exist: {RAW_FOLDER}"
        )

        return []

    files = sorted(
        [
            file.name
            for file in RAW_FOLDER.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".csv"
        ]
    )

    return files


# ================================================================
# MAIN
# ================================================================

def main():

    print()
    print("=" * 70)
    print("URL LOCATION & CATEGORY EXTRACTION SYSTEM")
    print("=" * 70)

    print()
    print(
        f"Raw Folder: {RAW_FOLDER}"
    )

    print(
        f"Output Folder: {OUTPUT_FOLDER}"
    )

    # ------------------------------------------------------------
    # Find files
    # ------------------------------------------------------------

    csv_files = find_csv_files()

    print()
    print(
        f"CSV files found: {len(csv_files)}"
    )

    if not csv_files:

        print()
        print(
            "No CSV files found in raw folder."
        )

        return

    for file_name in csv_files:

        print(
            f" - {file_name}"
        )

    # ------------------------------------------------------------
    # Process files
    # ------------------------------------------------------------

    successful = 0
    failed = 0

    for file_name in csv_files:

        try:

            result = process_file(
                file_name
            )

            if result:
                successful += 1
            else:
                failed += 1

        except Exception as error:

            failed += 1

            print()
            print("=" * 70)
            print(
                f"ERROR PROCESSING: {file_name}"
            )
            print("=" * 70)

            print(
                f"{type(error).__name__}: {error}"
            )

    # ------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------

    print()
    print("=" * 70)

    if failed == 0:

        print(
            "ALL CSV FILES PROCESSED SUCCESSFULLY"
        )

    else:

        print(
            "PROCESSING COMPLETED WITH SOME ERRORS"
        )

    print("=" * 70)

    print()
    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed:     {failed}"
    )

    print()
    print(
        f"Output folder:"
    )

    print(
        f"  {OUTPUT_FOLDER}"
    )

    print()


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    main()