# ================================================================
# URL EXTRACTION & CSV ENRICHMENT SYSTEM
# ================================================================
#
# INPUT:
#   data/raw/*.csv
#
# OUTPUT:
#   data/processed/*_enriched_new.csv
#
# OUTPUT COLUMNS:
#   No
#   Keyword
#   Volume
#   Position
#   Estimated Visits
#   CPC
#   Paid Difficulty
#   SEO Difficulty
#   Ranking URL
#   City
#   State
#   Country
#   Region
#   URL_Location
#   Area
#   Category
#   URL_Keyword
#   Unknown
#   Remaining_Url_Keywords
#   Priority Rank
#
# RULES:
#   1. Extract location only when it is present in the URL.
#   2. If not found, leave the field blank.
#   3. Category is extracted from the URL.
#   4. URL_Keyword contains important source-keyword words
#      that actually occur in the URL.
#   5. Location/category words are not repeated in URL_Keyword.
#   6. Remaining_Url_Keywords contains other useful URL words.
#   7. Priority Rank is always 1.
#
# ================================================================
import re
import html
from pathlib import Path
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

STATE_MAP = {

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

    # Union Territories
    "andaman and nicobar islands":
        "Andaman and Nicobar Islands",

    "andaman & nicobar islands":
        "Andaman and Nicobar Islands",

    "chandigarh":
        "Chandigarh",

    "dadra and nagar haveli and daman and diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "daman and diu":
        "Dadra and Nagar Haveli and Daman and Diu",

    "delhi":
        "Delhi",

    "nct of delhi":
        "Delhi",

    "national capital territory of delhi":
        "Delhi",

    "jammu and kashmir":
        "Jammu and Kashmir",

    "jammu & kashmir":
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
# REGION MAP
# ================================================================

REGION_MAP = {

    # North
    "Delhi": "North",
    "Haryana": "North",
    "Himachal Pradesh": "North",
    "Punjab": "North",
    "Rajasthan": "North",
    "Uttarakhand": "North",
    "Jammu and Kashmir": "North",
    "Ladakh": "North",
    "Chandigarh": "North",

    # South
    "Andhra Pradesh": "South",
    "Karnataka": "South",
    "Kerala": "South",
    "Tamil Nadu": "South",
    "Telangana": "South",
    "Puducherry": "South",

    # West
    "Goa": "West",
    "Gujarat": "West",
    "Maharashtra": "West",
    "Madhya Pradesh": "West",
    "Dadra and Nagar Haveli and Daman and Diu": "West",

    # East
    "Bihar": "East",
    "Jharkhand": "East",
    "Odisha": "East",
    "West Bengal": "East",
    "Sikkim": "East",

    # North East
    "Arunachal Pradesh": "North East",
    "Assam": "North East",
    "Manipur": "North East",
    "Meghalaya": "North East",
    "Mizoram": "North East",
    "Nagaland": "North East",
    "Tripura": "North East",

    # Central
    "Chhattisgarh": "Central",
}


# ================================================================
# COMMON INDIAN CITIES
# ================================================================

CITY_MAP = {

    # Delhi
    "new delhi": ("New Delhi", "Delhi"),
    "delhi": ("Delhi", "Delhi"),

    # Maharashtra
    "mumbai": ("Mumbai", "Maharashtra"),
    "bombay": ("Mumbai", "Maharashtra"),
    "pune": ("Pune", "Maharashtra"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "nashik": ("Nashik", "Maharashtra"),
    "nasik": ("Nashik", "Maharashtra"),
    "thane": ("Thane", "Maharashtra"),
    "kalyan": ("Kalyan", "Maharashtra"),
    "navi mumbai": ("Navi Mumbai", "Maharashtra"),
    "aurangabad": ("Aurangabad", "Maharashtra"),
    "chhatrapati sambhajinagar":
        ("Chhatrapati Sambhajinagar", "Maharashtra"),

    # Karnataka
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "mysore": ("Mysuru", "Karnataka"),
    "mysuru": ("Mysuru", "Karnataka"),
    "mangalore": ("Mangaluru", "Karnataka"),
    "mangaluru": ("Mangaluru", "Karnataka"),

    # Kerala
    "kochi": ("Kochi", "Kerala"),
    "cochin": ("Kochi", "Kerala"),
    "kottayam": ("Kottayam", "Kerala"),
    "thiruvananthapuram":
        ("Thiruvananthapuram", "Kerala"),
    "trivandrum":
        ("Thiruvananthapuram", "Kerala"),
    "kozhikode":
        ("Kozhikode", "Kerala"),
    "calicut":
        ("Kozhikode", "Kerala"),
    "kollam":
        ("Kollam", "Kerala"),
    "alappuzha":
        ("Alappuzha", "Kerala"),
    "alleppey":
        ("Alappuzha", "Kerala"),

    # Tamil Nadu
    "chennai":
        ("Chennai", "Tamil Nadu"),
    "madras":
        ("Chennai", "Tamil Nadu"),
    "coimbatore":
        ("Coimbatore", "Tamil Nadu"),
    "madurai":
        ("Madurai", "Tamil Nadu"),
    "salem":
        ("Salem", "Tamil Nadu"),
    "tiruchirappalli":
        ("Tiruchirappalli", "Tamil Nadu"),
    "trichy":
        ("Tiruchirappalli", "Tamil Nadu"),
    "tirunelveli":
        ("Tirunelveli", "Tamil Nadu"),
    "ooty":
        ("Ooty", "Tamil Nadu"),
    "udhagamandalam":
        ("Ooty", "Tamil Nadu"),

    # Telangana
    "hyderabad":
        ("Hyderabad", "Telangana"),
    "secunderabad":
        ("Secunderabad", "Telangana"),

    # Andhra Pradesh
    "tirupati":
        ("Tirupati", "Andhra Pradesh"),
    "visakhapatnam":
        ("Visakhapatnam", "Andhra Pradesh"),
    "vizag":
        ("Visakhapatnam", "Andhra Pradesh"),
    "vijayawada":
        ("Vijayawada", "Andhra Pradesh"),
    "guntur":
        ("Guntur", "Andhra Pradesh"),

    # Uttar Pradesh
    "lucknow":
        ("Lucknow", "Uttar Pradesh"),
    "kanpur":
        ("Kanpur", "Uttar Pradesh"),
    "agra":
        ("Agra", "Uttar Pradesh"),
    "varanasi":
        ("Varanasi", "Uttar Pradesh"),
    "banaras":
        ("Varanasi", "Uttar Pradesh"),
    "noida":
        ("Noida", "Uttar Pradesh"),
    "greater noida":
        ("Greater Noida", "Uttar Pradesh"),
    "ghaziabad":
        ("Ghaziabad", "Uttar Pradesh"),
    "meerut":
        ("Meerut", "Uttar Pradesh"),
    "mathura":
        ("Mathura", "Uttar Pradesh"),
    "vrindavan":
        ("Vrindavan", "Uttar Pradesh"),
    "prayagraj":
        ("Prayagraj", "Uttar Pradesh"),
    "allahabad":
        ("Prayagraj", "Uttar Pradesh"),

    # Rajasthan
    "jaipur":
        ("Jaipur", "Rajasthan"),
    "udaipur":
        ("Udaipur", "Rajasthan"),
    "jodhpur":
        ("Jodhpur", "Rajasthan"),
    "kota":
        ("Kota", "Rajasthan"),
    "ajmer":
        ("Ajmer", "Rajasthan"),
    "pushkar":
        ("Pushkar", "Rajasthan"),

    # Gujarat
    "ahmedabad":
        ("Ahmedabad", "Gujarat"),
    "surat":
        ("Surat", "Gujarat"),
    "vadodara":
        ("Vadodara", "Gujarat"),
    "baroda":
        ("Vadodara", "Gujarat"),
    "rajkot":
        ("Rajkot", "Gujarat"),
    "gandhinagar":
        ("Gandhinagar", "Gujarat"),

    # Goa
    "panaji":
        ("Panaji", "Goa"),
    "panjim":
        ("Panaji", "Goa"),
    "margao":
        ("Margao", "Goa"),
    "madgaon":
        ("Margao", "Goa"),
    "calangute":
        ("Calangute", "Goa"),
    "anjuna":
        ("Anjuna", "Goa"),
    "candolim":
        ("Candolim", "Goa"),
    "baga":
        ("Baga", "Goa"),

    # West Bengal
    "kolkata":
        ("Kolkata", "West Bengal"),
    "calcutta":
        ("Kolkata", "West Bengal"),
    "darjeeling":
        ("Darjeeling", "West Bengal"),

    # Bihar
    "patna":
        ("Patna", "Bihar"),
    "gaya":
        ("Gaya", "Bihar"),

    # Punjab
    "amritsar":
        ("Amritsar", "Punjab"),
    "ludhiana":
        ("Ludhiana", "Punjab"),
    "chandigarh":
        ("Chandigarh", "Chandigarh"),

    # Haryana
    "gurgaon":
        ("Gurugram", "Haryana"),
    "gurugram":
        ("Gurugram", "Haryana"),
    "faridabad":
        ("Faridabad", "Haryana"),

    # Odisha
    "bhubaneswar":
        ("Bhubaneswar", "Odisha"),
    "puri":
        ("Puri", "Odisha"),
    "cuttack":
        ("Cuttack", "Odisha"),

    # Madhya Pradesh
    "indore":
        ("Indore", "Madhya Pradesh"),
    "bhopal":
        ("Bhopal", "Madhya Pradesh"),
    "gwalior":
        ("Gwalior", "Madhya Pradesh"),
    "jabalpur":
        ("Jabalpur", "Madhya Pradesh"),

    # Jharkhand
    "ranchi":
        ("Ranchi", "Jharkhand"),
    "jamshedpur":
        ("Jamshedpur", "Jharkhand"),

    # Chhattisgarh
    "raipur":
        ("Raipur", "Chhattisgarh"),

    # Uttarakhand
    "dehradun":
        ("Dehradun", "Uttarakhand"),
    "rishikesh":
        ("Rishikesh", "Uttarakhand"),
    "nainital":
        ("Nainital", "Uttarakhand"),
    "haridwar":
        ("Haridwar", "Uttarakhand"),

    # Jammu & Kashmir
    "srinagar":
        ("Srinagar", "Jammu and Kashmir"),
    "jammu":
        ("Jammu", "Jammu and Kashmir"),

    # Himachal Pradesh
    "shimla":
        ("Shimla", "Himachal Pradesh"),
    "manali":
        ("Manali", "Himachal Pradesh"),
    "dharamshala":
        ("Dharamshala", "Himachal Pradesh"),

    # Assam
    "guwahati":
        ("Guwahati", "Assam"),
}


SORTED_CITIES = sorted(
    CITY_MAP.items(),
    key=lambda x: len(x[0]),
    reverse=True
)


# ================================================================
# AREA / LOCALITY MAP
# ================================================================

AREA_WORDS = {

    # Delhi
    "connaught place": "Connaught Place",
    "karol bagh": "Karol Bagh",
    "rohini": "Rohini",
    "dwarka": "Dwarka",
    "saket": "Saket",
    "hauz khas": "Hauz Khas",
    "lajpat nagar": "Lajpat Nagar",
    "greater kailash": "Greater Kailash",
    "gk": "Greater Kailash",
    "sector 18": "Sector 18",
    "sector 62": "Sector 62",
    "sector 63": "Sector 63",
    "sector 15": "Sector 15",
    "vasant kunj": "Vasant Kunj",
    "india gate": "India Gate",
    "chandni chowk": "Chandni Chowk",
    "old delhi": "Old Delhi",
    "new friends colony": "New Friends Colony",

    # Common India
    "mg road": "MG Road",
    "marine drive": "Marine Drive",
    "bandra": "Bandra",
    "andheri": "Andheri",
    "colaba": "Colaba",
    "juhu": "Juhu",
    "powai": "Powai",

    # Bengaluru
    "koramangala": "Koramangala",
    "indiranagar": "Indiranagar",
    "whitefield": "Whitefield",
    "electronic city": "Electronic City",
}


SORTED_AREAS = sorted(
    AREA_WORDS.items(),
    key=lambda x: len(x[0]),
    reverse=True
)


# ================================================================
# CATEGORY KEYWORDS
# ================================================================

CATEGORY_URL_WORDS = {

    "Restaurant": [
        "restaurant_review",
        "restaurantsnear",
        "restaurants",
        "restaurant",
        "dining",
        "food",
        "cafe",
        "cafes",
        "eatery",
        "eateries",
        "bar",
        "bars",
    ],

    "Hotel": [
        "hotels",
        "hotel",
        "accommodation",
        "resort",
        "resorts",
        "stay",
        "stays",
        "lodging",
    ],

    "Attraction": [
        "attraction_review",
        "attractions",
        "activities",
        "things_to_do",
        "thingstodo",
        "places_to_visit",
        "places-to-visit",
        "sightseeing",
        "landmarks",
    ],

    "Tourism": [
        "tourism",
        "vacations",
        "vacation",
        "travel",
        "trip",
        "trips",
        "tour",
        "tours",
    ],
}


# ================================================================
# URL STOP WORDS
# ================================================================

URL_STOP_WORDS = {

    "www",
    "com",
    "in",
    "org",
    "net",
    "co",
    "india",

    "the",
    "and",
    "or",
    "of",
    "for",
    "with",
    "from",
    "near",

    "reviews",
    "review",
    "listing",
    "listings",
    "directory",
    "search",

    "page",
    "pages",
    "html",
    "htm",
    "php",
    "aspx",

    "amp",
}


# ================================================================
# NORMALIZE URL
# ================================================================

def normalize_url(value):

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    url = str(value).strip()

    if not url:
        return ""

    # Decode HTML entities
    url = html.unescape(url)

    # Extract URL from markdown
    markdown_match = re.search(
        r'https?://[^\s\)\]\>]+',
        url,
        flags=re.IGNORECASE
    )

    if markdown_match:
        url = markdown_match.group(0)

    # Decode URL
    url = unquote(url)

    # Clean
    url = url.strip(
        ' <>"\''
    )

    url = url.rstrip(
        ".,;"
    )

    return url


# ================================================================
# NORMALIZE TEXT
# ================================================================

def normalize_text(text):

    if text is None:
        return ""

    text = unquote(
        str(text)
    )

    text = html.unescape(
        text
    )

    text = text.lower()

    text = text.replace(
        "-",
        " "
    )

    text = text.replace(
        "_",
        " "
    )

    text = text.replace(
        "/",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ================================================================
# GET URL PATH
# ================================================================

def get_url_path(url):

    if not url:
        return ""

    try:

        parsed = urlparse(
            url
        )

        path = parsed.path

        return unquote(
            path
        )

    except Exception:

        return url


# ================================================================
# GET SEARCHABLE URL TEXT
# ================================================================

def get_search_text(url):

    path = get_url_path(
        url
    )

    return normalize_text(
        path
    )


# ================================================================
# FIND STATE
# ================================================================

def extract_state(url):

    text = get_search_text(
        url
    )

    if not text:
        return ""

    states = sorted(
        STATE_MAP.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for state_key, state_name in states:

        pattern = (
            r"\b"
            + re.escape(state_key)
            + r"\b"
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return state_name

    return ""


# ================================================================
# FIND CITY
# ================================================================

def find_city(
    text,
    detected_state=""
):

    if not text:
        return ""

    text = normalize_text(
        text
    )

    for city_key, city_info in SORTED_CITIES:

        city_name, city_state = city_info

        # If state is known, make sure city belongs to it
        if (
            detected_state
            and city_state != detected_state
        ):
            continue

        pattern = (
            r"\b"
            + re.escape(city_key)
            + r"\b"
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return city_name

    return ""


# ================================================================
# CITY EXTRACTION
# ================================================================

def extract_city(
    url,
    state
):

    text = get_search_text(
        url
    )

    if not text:
        return ""

    # First try known city
    city = find_city(
        text,
        state
    )

    if city:
        return city

    return ""


# ================================================================
# COUNTRY EXTRACTION
# ================================================================

def extract_country(
    url,
    state
):

    text = get_search_text(
        url
    )

    if not text:
        return ""

    # Only return country if India is actually present
    if re.search(
        r"\bindia\b",
        text,
        flags=re.IGNORECASE
    ):
        return "India"

    # If an Indian state/city was explicitly detected,
    # country can reasonably be identified as India.
    if state:
        return "India"

    return ""


# ================================================================
# REGION EXTRACTION
# ================================================================

def extract_region(
    state
):

    if not state:
        return ""

    return REGION_MAP.get(
        state,
        ""
    )


# ================================================================
# URL LOCATION
# ================================================================

def extract_url_location(
    city,
    area
):

    # City gets priority
    if city:
        return city

    if area:
        return area

    return ""


# ================================================================
# CATEGORY EXTRACTION
# ================================================================

def extract_category(url):

    text = get_search_text(
        url
    )

    if not text:
        return ""

    # Check categories in priority order
    for category, patterns in CATEGORY_URL_WORDS.items():

        for pattern in patterns:

            pattern_normalized = normalize_text(
                pattern
            )

            regex = (
                r"\b"
                + re.escape(pattern_normalized)
                + r"\b"
            )

            if re.search(
                regex,
                text,
                flags=re.IGNORECASE
            ):
                return category

    return ""


# ================================================================
# AREA EXTRACTION
# ================================================================

def extract_area(url):

    text = get_search_text(
        url
    )

    if not text:
        return ""

    for area_key, area_name in SORTED_AREAS:

        pattern = (
            r"\b"
            + re.escape(area_key)
            + r"\b"
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            return area_name

    return ""


# ================================================================
# URL TOKENS
# ================================================================

def url_tokens(url):

    path = get_url_path(
        url
    )

    if not path:
        return []

    # Remove extensions
    path = re.sub(
        r"\.(html?|php|aspx?)$",
        "",
        path,
        flags=re.IGNORECASE
    )

    # Convert separators to spaces
    path = re.sub(
        r"[-_/]+",
        " ",
        path
    )

    # Normalize
    path = normalize_text(
        path
    )

    # Extract words
    tokens = re.findall(
        r"[a-z0-9]+",
        path
    )

    # Remove useless URL words
    cleaned_tokens = []

    for token in tokens:

        if token in URL_STOP_WORDS:
            continue

        if len(token) <= 1:
            continue

        cleaned_tokens.append(
            token
        )

    return cleaned_tokens


# ================================================================
# TOKEN SET FROM LOCATION / CATEGORY
# ================================================================

def metadata_tokens(
    url,
    city,
    state,
    country,
    region,
    area,
    category
):

    text = get_search_text(
        url
    )

    words = set()

    # ------------------------------------------------------------
    # City
    # ------------------------------------------------------------

    if city:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(city)
            )
        )

    # ------------------------------------------------------------
    # State
    # ------------------------------------------------------------

    if state:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(state)
            )
        )

    # ------------------------------------------------------------
    # Country
    # ------------------------------------------------------------

    if country:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(country)
            )
        )

    # ------------------------------------------------------------
    # Region
    # ------------------------------------------------------------

    if region:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(region)
            )
        )

    # ------------------------------------------------------------
    # Area
    # ------------------------------------------------------------

    if area:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(area)
            )
        )

    # ------------------------------------------------------------
    # Category
    # ------------------------------------------------------------

    if category:

        words.update(
            re.findall(
                r"[a-z0-9]+",
                normalize_text(category)
            )
        )

        # Add category URL words actually found in URL
        if category in CATEGORY_URL_WORDS:

            for category_word in CATEGORY_URL_WORDS[category]:

                normalized_category_word = normalize_text(
                    category_word
                )

                if normalized_category_word in text:

                    words.update(
                        re.findall(
                            r"[a-z0-9]+",
                            normalized_category_word
                        )
                    )

    # ------------------------------------------------------------
    # Explicit URL metadata words
    # ------------------------------------------------------------

    words.update(
        {
            "india",
            "north",
            "south",
            "east",
            "west",
            "central",
            "northeast",
        }
    )

    return words


# ================================================================
# URL KEYWORD EXTRACTION
# ================================================================

def extract_url_keywords(
    url,
    keyword,
    city,
    state,
    country,
    region,
    area,
    category
):

    tokens = url_tokens(
        url
    )

    if not tokens:

        return "", ""

    # Metadata words are NOT considered keyword
    metadata = metadata_tokens(
        url,
        city,
        state,
        country,
        region,
        area,
        category
    )

    # ------------------------------------------------------------
    # Original source keyword
    # ------------------------------------------------------------

    keyword_tokens = re.findall(
        r"[a-z0-9]+",
        normalize_text(keyword)
    )

    # ------------------------------------------------------------
    # URL keyword
    # ------------------------------------------------------------

    remaining_tokens = tokens.copy()

    matched_keyword = []

    for token in keyword_tokens:

        # Do not duplicate metadata
        if token in metadata:
            continue

        if token in remaining_tokens:

            matched_keyword.append(
                token
            )

            remaining_tokens.remove(
                token
            )

    # ------------------------------------------------------------
    # Important behavior:
    #
    # If the original Keyword does not match the URL,
    # do NOT blindly put the first random URL word
    # into URL_Keyword.
    #
    # Instead, keep URL_Keyword blank and put meaningful
    # remaining URL words into Remaining_Url_Keywords.
    # ------------------------------------------------------------

    url_keyword = " ".join(
        matched_keyword
    ).strip()

    # ------------------------------------------------------------
    # Remaining URL keywords
    # ------------------------------------------------------------

    remaining_meaningful = []

    for token in remaining_tokens:

        if token in metadata:
            continue

        if token in URL_STOP_WORDS:
            continue

        if len(token) <= 1:
            continue

        remaining_meaningful.append(
            token
        )

    remaining_keyword = " ".join(
        remaining_meaningful
    ).strip()

    return (
        url_keyword,
        remaining_keyword
    )


# ================================================================
# BUSINESS CATEGORY / PRODUCT CATEGORY / SOURCE
# ================================================================

BUSINESS_CATEGORY_MAP = {
    "Restaurant": "Food & Dining",
    "Hotel": "Accommodation",
    "Attraction": "Tourism & Attractions",
    "Tourism": "Travel & Tourism",
}

PRODUCT_CATEGORY_URL_WORDS = {
    "Food & Dining": [
        "restaurant", "restaurants", "food", "cafe", "cafes",
        "dining", "eatery", "eateries", "bar", "bars"
    ],
    "Accommodation": [
        "hotel", "hotels", "resort", "resorts", "stay",
        "stays", "lodging", "accommodation"
    ],
    "Tourism": [
        "tourism", "travel", "trip", "trips", "tour", "tours",
        "vacation", "vacations"
    ],
    "Attractions": [
        "attraction", "attractions", "activities", "things_to_do",
        "thingstodo", "places_to_visit", "places-to-visit",
        "sightseeing", "landmarks"
    ],
}


def extract_business_category(category):
    """Map the existing URL Category to a broader business category."""
    return BUSINESS_CATEGORY_MAP.get(category, "")


def extract_product_category(url, keyword="", category=""):
    """Extract a product/service category from URL and source keyword."""
    text = get_search_text(url)

    if not text:
        text = normalize_text(keyword)

    # Check the existing URL category first.
    category_mapping = {
        "Restaurant": "Food & Dining",
        "Hotel": "Accommodation",
        "Attraction": "Attractions",
        "Tourism": "Tourism",
    }

    if category in category_mapping:
        return category_mapping[category]

    # Fall back to URL/source-keyword words.
    for product_category, patterns in PRODUCT_CATEGORY_URL_WORDS.items():
        for pattern in patterns:
            if re.search(
                r"\b" + re.escape(normalize_text(pattern)) + r"\b",
                text,
                flags=re.IGNORECASE
            ):
                return product_category

    return ""


def extract_source(url):
    """Extract the source website/domain from the Ranking URL."""
    clean_url = normalize_url(url)

    if not clean_url:
        return ""

    try:
        parsed = urlparse(clean_url)
        domain = parsed.netloc.lower().strip()

        # Remove www. from the source name.
        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


# ================================================================
# COMPLETE URL EXTRACTION
# ================================================================

def extract_location_data(
    url,
    keyword=""
):

    clean_url = normalize_url(
        url
    )

    # Empty URL
    if not clean_url:

        return {

            "City": "",
            "State": "",
            "Country": "",
            "Region": "",
            "URL_Location": "",
            "Area": "",
            "Category": "",
            "Business Category": "",
            "Product Category": "",
            "Source": "",
            "URL_Keyword": "",
            "Unknown": "",
            "Remaining_Url_Keywords": "",
            "Priority Rank": 1,

        }

    # ------------------------------------------------------------
    # State
    # ------------------------------------------------------------

    state = extract_state(
        clean_url
    )

    # ------------------------------------------------------------
    # City
    # ------------------------------------------------------------

    city = extract_city(
        clean_url,
        state
    )

    # ------------------------------------------------------------
    # Area
    # ------------------------------------------------------------

    area = extract_area(
        clean_url
    )

    # ------------------------------------------------------------
    # Country
    # ------------------------------------------------------------

    country = extract_country(
        clean_url,
        state
    )

    # ------------------------------------------------------------
    # Region
    # ------------------------------------------------------------

    region = extract_region(
        state
    )

    # ------------------------------------------------------------
    # URL Location
    # ------------------------------------------------------------

    url_location = extract_url_location(
        city,
        area
    )

    # ------------------------------------------------------------
    # Category
    # ------------------------------------------------------------

    category = extract_category(
        clean_url
    )

    # ------------------------------------------------------------
    # Business Category
    # ------------------------------------------------------------

    business_category = extract_business_category(
        category
    )

    # ------------------------------------------------------------
    # Product Category
    # ------------------------------------------------------------

    product_category = extract_product_category(
        clean_url,
        keyword,
        category
    )

    # ------------------------------------------------------------
    # Source
    # ------------------------------------------------------------

    source = extract_source(
        clean_url
    )

    # ------------------------------------------------------------
    # URL Keyword
    # ------------------------------------------------------------

    url_keyword, remaining_url_keywords = extract_url_keywords(
        clean_url,
        keyword,
        city,
        state,
        country,
        region,
        area,
        category
    )

    # ------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------

    return {

        "City": city,

        "State": state,

        "Country": country,

        "Region": region,

        "URL_Location": url_location,

        "Area": area,

        "Category": category,

        "Business Category": business_category,

        "Product Category": product_category,

        "Source": source,

        "URL_Keyword": url_keyword,

        "Unknown": "",

        "Remaining_Url_Keywords":
            remaining_url_keywords,

        "Priority Rank": 1,
    }


# ================================================================
# FIND URL COLUMN
# ================================================================

def find_url_column(df):

    possible_columns = [

        "Ranking URL",
        "Ranking_URL",
        "RankingURL",
        "URL",
        "url",
        "Url",
        "ranking_url",
        "ranking url",

    ]

    # Exact match
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

        if (
            "ranking" in normalized
            and "url" in normalized
        ):
            return column

        if normalized == "url":
            return column

    return None


# ================================================================
# READ CSV SAFELY
# ================================================================

def read_csv_safely(
    file_path
):

    encodings = [

        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",

    ]

    last_error = None

    for encoding in encodings:

        try:

            return pd.read_csv(
                file_path,
                encoding=encoding,
                low_memory=False
            )

        except Exception as error:

            last_error = error

    raise last_error


# ================================================================
# COLUMN ORDER
# ================================================================

def arrange_columns(df):

    required_order = [

        "No",
        "Keyword",
        "Volume",
        "Position",
        "Estimated Visits",
        "CPC",
        "Paid Difficulty",
        "SEO Difficulty",
        "Ranking URL",

        "City",
        "State",
        "Country",
        "Region",
        "URL_Location",
        "Area",
        "Category",
        "Business Category",
        "Product Category",
        "Source",

        "URL_Keyword",
        "Unknown",
        "Remaining_Url_Keywords",

        "Priority Rank",

    ]

    # Make sure required columns exist
    for column in required_order:

        if column not in df.columns:

            if column == "Priority Rank":

                df[column] = 1

            else:

                df[column] = ""

    # Keep only desired order + any original extra columns
    existing = [

        column
        for column in required_order
        if column in df.columns

    ]

    remaining = [

        column
        for column in df.columns
        if column not in existing

    ]

    return df[
        existing + remaining
    ]


# ================================================================
# SAVE CSV
# ================================================================

def save_csv(
    df,
    output_path
):

    try:

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print()
        print("Output saved successfully:")
        print(output_path)

        return output_path

    except PermissionError:

        print()
        print("WARNING: Output file is locked.")
        print("Trying alternate filename...")

        new_path = output_path.with_name(
            output_path.stem
            + "_new.csv"
        )

        try:

            df.to_csv(
                new_path,
                index=False,
                encoding="utf-8-sig"
            )

            print()
            print("Output saved as:")
            print(new_path)

            return new_path

        except Exception as error:

            print()
            print("ERROR saving file:")
            print(error)

            return None


# ================================================================
# PROCESS ONE CSV
# ================================================================

def process_file(
    file_path
):

    print()
    print("=" * 80)
    print("PROCESSING:", file_path.name)
    print("=" * 80)

    # ------------------------------------------------------------
    # READ CSV
    # ------------------------------------------------------------

    try:

        df = read_csv_safely(
            file_path
        )

    except Exception as error:

        print("ERROR reading CSV:")
        print(error)

        return False

    print()
    print("Original Shape:")
    print(df.shape)

    print()
    print("Original Columns:")
    print(list(df.columns))

    # ------------------------------------------------------------
    # URL COLUMN
    # ------------------------------------------------------------

    url_column = find_url_column(
        df
    )

    if url_column is None:

        print()
        print(
            "ERROR: Ranking URL column not found."
        )

        print()
        print("Available columns:")

        for column in df.columns:
            print(" -", column)

        return False

    print()
    print("URL Column:")
    print(url_column)

    # ------------------------------------------------------------
    # KEYWORD COLUMN
    # ------------------------------------------------------------

    if "Keyword" not in df.columns:

        print()
        print(
            "WARNING: Keyword column not found."
        )

        df["Keyword"] = ""

    # ------------------------------------------------------------
    # EXTRACT URL DATA
    # ------------------------------------------------------------

    results = []

    total = len(
        df
    )

    print()
    print(
        "Extracting URL information..."
    )

    for index, row in df.iterrows():

        url = row.get(
            url_column,
            ""
        )

        keyword = row.get(
            "Keyword",
            ""
        )

        result = extract_location_data(
            url,
            keyword
        )

        results.append(
            result
        )

        current = index + 1

        if (
            current % 500 == 0
            or current == total
        ):

            print(
                f"Processed "
                f"{current:,}/{total:,}"
            )

    # ------------------------------------------------------------
    # RESULT DATAFRAME
    # ------------------------------------------------------------

    result_df = pd.DataFrame(
        results
    )

    # ------------------------------------------------------------
    # ADD COLUMNS
    # ------------------------------------------------------------

    df["City"] = result_df[
        "City"
    ]

    df["State"] = result_df[
        "State"
    ]

    df["Country"] = result_df[
        "Country"
    ]

    df["Region"] = result_df[
        "Region"
    ]

    df["URL_Location"] = result_df[
        "URL_Location"
    ]

    df["Area"] = result_df[
        "Area"
    ]

    df["Category"] = result_df[
        "Category"
    ]

    df["Business Category"] = result_df[
        "Business Category"
    ]

    df["Product Category"] = result_df[
        "Product Category"
    ]

    df["Source"] = result_df[
        "Source"
    ]

    df["URL_Keyword"] = result_df[
        "URL_Keyword"
    ]

    df["Unknown"] = result_df[
        "Unknown"
    ]

    df["Remaining_Url_Keywords"] = result_df[
        "Remaining_Url_Keywords"
    ]

    # ------------------------------------------------------------
    # PRIORITY RANK = 1 FOR ALL
    # ------------------------------------------------------------

    df["Priority Rank"] = 1

    # ------------------------------------------------------------
    # ARRANGE COLUMNS
    # ------------------------------------------------------------

    df = arrange_columns(
        df
    )

    # ------------------------------------------------------------
    # EXTRACTION SUMMARY
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)

    print()
    print("CITY DISTRIBUTION:")

    print(
        df["City"]
        .replace("", "Blank")
        .value_counts()
        .head(20)
    )

    print()
    print("STATE DISTRIBUTION:")

    print(
        df["State"]
        .replace("", "Blank")
        .value_counts()
        .head(20)
    )

    print()
    print("REGION DISTRIBUTION:")

    print(
        df["Region"]
        .replace("", "Blank")
        .value_counts()
    )

    print()
    print("CATEGORY DISTRIBUTION:")

    print(
        df["Category"]
        .replace("", "Blank")
        .value_counts()
    )

    # ------------------------------------------------------------
    # MATCH RATES
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print("MATCH RATES")
    print("=" * 80)

    for column in [

        "City",
        "State",
        "Country",
        "Region",
        "URL_Location",
        "Area",
        "Category",
        "URL_Keyword",
        "Remaining_Url_Keywords",

    ]:

        non_blank = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        )

        if len(df) > 0:

            rate = (
                non_blank
                / len(df)
            ) * 100

        else:

            rate = 0

        print(
            f"{column}: "
            f"{non_blank:,}/{len(df):,} "
            f"({rate:.2f}%)"
        )

    # ------------------------------------------------------------
    # BLANK COUNTS
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print("BLANK COUNTS")
    print("=" * 80)

    for column in [

        "City",
        "State",
        "Country",
        "Region",
        "URL_Location",
        "Area",
        "Category",
        "URL_Keyword",
        "Remaining_Url_Keywords",

    ]:

        blank_count = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        print(
            f"{column}: "
            f"{blank_count:,}"
        )

    # ------------------------------------------------------------
    # PRIORITY CHECK
    # ------------------------------------------------------------

    print()
    print("PRIORITY RANK:")

    print(
        df["Priority Rank"]
        .value_counts()
        .sort_index()
    )

    # ------------------------------------------------------------
    # OUTPUT FILE
    # ------------------------------------------------------------

    output_name = (
        file_path.stem
        + "_enriched_new.csv"
    )

    output_path = (
        OUTPUT_FOLDER
        / output_name
    )

    # ------------------------------------------------------------
    # SAVE
    # ------------------------------------------------------------

    saved = save_csv(
        df,
        output_path
    )

    if saved is None:
        return False

    # ------------------------------------------------------------
    # FINAL SHAPE
    # ------------------------------------------------------------

    print()
    print("Final Shape:")
    print(df.shape)

    print()
    print("Final Columns:")

    for index, column in enumerate(
        df.columns,
        start=1
    ):

        print(
            f"{index}. {column}"
        )

    return True


# ================================================================
# FIND CSV FILES
# ================================================================

def find_csv_files():

    if not RAW_FOLDER.exists():

        print()
        print("ERROR:")
        print(
            "Raw folder does not exist:"
        )
        print(
            RAW_FOLDER
        )

        return []

    files = sorted(
        [
            file
            for file in RAW_FOLDER.iterdir()
            if (
                file.is_file()
                and file.suffix.lower() == ".csv"
            )
        ]
    )

    return files


# ================================================================
# MAIN
# ================================================================

def main():

    print()
    print("=" * 80)
    print(
        "URL LOCATION & CATEGORY EXTRACTION SYSTEM"
    )
    print("=" * 80)

    print()
    print("Raw Folder:")
    print(
        RAW_FOLDER
    )

    print()
    print("Output Folder:")
    print(
        OUTPUT_FOLDER
    )

    # ------------------------------------------------------------
    # FIND CSV FILES
    # ------------------------------------------------------------

    csv_files = find_csv_files()

    print()
    print(
        f"CSV files found: "
        f"{len(csv_files)}"
    )

    if not csv_files:

        print()
        print(
            "No CSV files found."
        )

        print()
        print(
            "Put your CSV files inside:"
        )

        print(
            RAW_FOLDER
        )

        return

    print()

    for file in csv_files:

        print(
            " -",
            file.name
        )

    # ------------------------------------------------------------
    # PROCESS FILES
    # ------------------------------------------------------------

    successful = 0
    failed = 0

    for file_path in csv_files:

        try:

            success = process_file(
                file_path
            )

            if success:

                successful += 1

            else:

                failed += 1

        except Exception as error:

            failed += 1

            print()
            print(
                "ERROR processing:",
                file_path.name
            )

            print(
                type(error).__name__,
                ":",
                error
            )

    # ------------------------------------------------------------
    # FINAL REPORT
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print("FINAL REPORT")
    print("=" * 80)

    print()
    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print()
    print(
        "Completed."
    )


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    main()
