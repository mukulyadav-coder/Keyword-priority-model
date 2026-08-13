import pandas as pd
import os
import re
from urllib.parse import urlparse, unquote


# ============================================================
# CONFIGURATION
# ============================================================

RAW_FOLDER = "data/raw"
OUTPUT_FOLDER = "data/processed"

URL_COLUMN = "Ranking URL"


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# CITY / STATE / COUNTRY REFERENCE
# ============================================================

LOCATION_DATA = {

    # Maharashtra
    "mumbai": {
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India"
    },

    "pune": {
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India"
    },

    "nagpur": {
        "city": "Nagpur",
        "state": "Maharashtra",
        "country": "India"
    },

    # Karnataka
    "bangalore": {
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India"
    },

    "bengaluru": {
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India"
    },

    # Delhi / NCR
    "delhi": {
        "city": "Delhi",
        "state": "Delhi",
        "country": "India"
    },

    "new-delhi": {
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India"
    },

    # Telangana
    "hyderabad": {
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India"
    },

    # Tamil Nadu
    "chennai": {
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India"
    },

    # West Bengal
    "kolkata": {
        "city": "Kolkata",
        "state": "West Bengal",
        "country": "India"
    },

    # Gujarat
    "ahmedabad": {
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India"
    },

    "surat": {
        "city": "Surat",
        "state": "Gujarat",
        "country": "India"
    },

    # Rajasthan
    "jaipur": {
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India"
    },

    # Uttar Pradesh
    "lucknow": {
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "country": "India"
    },

    "agra": {
        "city": "Agra",
        "state": "Uttar Pradesh",
        "country": "India"
    },

    "varanasi": {
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "country": "India"
    },

    # Kerala
    "kochi": {
        "city": "Kochi",
        "state": "Kerala",
        "country": "India"
    },

    # Madhya Pradesh
    "indore": {
        "city": "Indore",
        "state": "Madhya Pradesh",
        "country": "India"
    },

    # Bihar
    "patna": {
        "city": "Patna",
        "state": "Bihar",
        "country": "India"
    },

    # Uttarakhand
    "dehradun": {
        "city": "Dehradun",
        "state": "Uttarakhand",
        "country": "India"
    },

    # Goa
    "goa": {
        "city": "Goa",
        "state": "Goa",
        "country": "India"
    },

    # Chandigarh
    "chandigarh": {
        "city": "Chandigarh",
        "state": "Chandigarh",
        "country": "India"
    }
}


# ============================================================
# REGION REFERENCE
# ============================================================

REGION_DATA = {

    "ncr": "NCR",

    "delhi-ncr": "Delhi NCR",

    "national-capital-region": "NCR",

    "north-india": "North India",

    "south-india": "South India",

    "east-india": "East India",

    "west-india": "West India",

    "central-india": "Central India"
}


# ============================================================
# CATEGORY REFERENCE
# ============================================================

CATEGORY_DATA = {

    "restaurants-near-me": "Restaurant",

    "restaurant-near-me": "Restaurant",

    "restaurants": "Restaurant",

    "restaurant": "Restaurant",

    "cafes-near-me": "Cafe",

    "cafes": "Cafe",

    "cafe": "Cafe",

    "bars-near-me": "Bar",

    "bars": "Bar",

    "bar": "Bar",

    "bakeries-near-me": "Bakery",

    "bakeries": "Bakery",

    "bakery": "Bakery",

    "hotels": "Hotel",

    "hotel": "Hotel",

    "desserts": "Dessert",

    "dessert": "Dessert",

    "pizza": "Pizza",

    "coffee": "Coffee",

    "sweet-shop": "Sweet Shop",

    "ice-cream": "Ice Cream",

    "fast-food": "Fast Food"
}


# ============================================================
# URL CLEANING
# ============================================================

def clean_url(url):

    if pd.isna(url):
        return ""

    url = str(url).strip()

    if not url:
        return ""

    return url


# ============================================================
# GET URL PATH PARTS
# ============================================================

def get_url_parts(url):

    url = clean_url(url)

    if not url:
        return []

    try:

        parsed_url = urlparse(url)

        path = unquote(parsed_url.path)

        path = path.strip("/")

        if not path:
            return []

        parts = path.split("/")

        cleaned_parts = []

        for part in parts:

            part = part.strip().lower()

            if part:
                cleaned_parts.append(part)

        return cleaned_parts

    except Exception:

        return []


# ============================================================
# GET COMPLETE URL PATH
# ============================================================

def extract_url_path(url):

    url = clean_url(url)

    if not url:
        return "Unknown"

    try:

        parsed_url = urlparse(url)

        path = unquote(parsed_url.path)

        if not path:
            return "Unknown"

        return path

    except Exception:

        return "Unknown"


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = str(text).lower()

    text = text.replace("_", "-")

    text = text.strip()

    return text


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(url):

    parts = get_url_parts(url)

    result = {

        "City": "Unknown",

        "State": "Unknown",

        "Country": "Unknown",

        "Region": "Unknown",

        "URL_Location": "Unknown"
    }

    if not parts:

        return result

    # --------------------------------------------------------
    # Check Region
    # --------------------------------------------------------

    for part in parts:

        part_normalized = normalize_text(part)

        if part_normalized in REGION_DATA:

            result["Region"] = REGION_DATA[
                part_normalized
            ]

            result["URL_Location"] = part

    # --------------------------------------------------------
    # Check City
    # --------------------------------------------------------

    for part in parts:

        part_normalized = normalize_text(part)

        if part_normalized in LOCATION_DATA:

            location = LOCATION_DATA[
                part_normalized
            ]

            result["City"] = location["city"]

            result["State"] = location["state"]

            result["Country"] = location["country"]

            result["URL_Location"] = part

            return result

    # --------------------------------------------------------
    # If Region exists but City doesn't
    # --------------------------------------------------------

    if result["Region"] != "Unknown":

        result["Country"] = "India"

    return result


# ============================================================
# EXTRACT CATEGORY
# ============================================================

def extract_category(url):

    parts = get_url_parts(url)

    result = {

        "Category": "Unknown",

        "URL_Category": "Unknown"
    }

    if not parts:

        return result

    # --------------------------------------------------------
    # First check exact category patterns
    # --------------------------------------------------------

    for part in parts:

        part_normalized = normalize_text(part)

        if part_normalized in CATEGORY_DATA:

            result["Category"] = CATEGORY_DATA[
                part_normalized
            ]

            result["URL_Category"] = part

            return result

    # --------------------------------------------------------
    # Check complete path
    # --------------------------------------------------------

    full_path = "/".join(parts)

    for pattern, category in CATEGORY_DATA.items():

        if pattern in full_path:

            result["Category"] = category

            result["URL_Category"] = pattern

            return result

    return result


# ============================================================
# PROCESS ONE CSV FILE
# ============================================================

def process_file(file_name):

    print("\n" + "=" * 70)

    print("Processing:", file_name)

    print("=" * 70)

    input_path = os.path.join(
        RAW_FOLDER,
        file_name
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            input_path,
            encoding="latin1"
        )

    except Exception as error:

        print(
            "Error loading file:",
            error
        )

        return

    print(
        "Original Shape:",
        df.shape
    )

    # --------------------------------------------------------
    # CHECK URL COLUMN
    # --------------------------------------------------------

    if URL_COLUMN not in df.columns:

        print(
            "\nERROR:"
        )

        print(
            f"'{URL_COLUMN}' column not found."
        )

        print(
            "Available columns:"
        )

        print(
            df.columns.tolist()
        )

        return

    # --------------------------------------------------------
    # LOCATION EXTRACTION
    # --------------------------------------------------------

    location_results = (
        df[URL_COLUMN]
        .apply(extract_location)
    )

    location_df = pd.DataFrame(
        location_results.tolist()
    )

    # --------------------------------------------------------
    # CATEGORY EXTRACTION
    # --------------------------------------------------------

    category_results = (
        df[URL_COLUMN]
        .apply(extract_category)
    )

    category_df = pd.DataFrame(
        category_results.tolist()
    )

    # --------------------------------------------------------
    # ADD NEW COLUMNS
    # --------------------------------------------------------

    df["City"] = location_df["City"]

    df["State"] = location_df["State"]

    df["Country"] = location_df["Country"]

    df["Region"] = location_df["Region"]

    df["URL_Location"] = location_df[
        "URL_Location"
    ]

    df["Category"] = category_df[
        "Category"
    ]

    df["URL_Category"] = category_df[
        "URL_Category"
    ]

    df["URL_Path"] = (
        df[URL_COLUMN]
        .apply(extract_url_path)
    )

    # --------------------------------------------------------
    # KEEP ORIGINAL COLUMNS FIRST
    # --------------------------------------------------------

    original_columns = [
        column
        for column in df.columns
        if column not in [

            "City",

            "State",

            "Country",

            "Region",

            "URL_Location",

            "Category",

            "URL_Category",

            "URL_Path"
        ]
    ]

    new_columns = [

        "City",

        "State",

        "Country",

        "Region",

        "URL_Location",

        "Category",

        "URL_Category",

        "URL_Path"
    ]

    df = df[
        original_columns
        + new_columns
    ]

    # --------------------------------------------------------
    # DISPLAY SAMPLE
    # --------------------------------------------------------

    print("\nSample extracted data:")

    print(

        df[
            [
                URL_COLUMN,

                "City",

                "State",

                "Country",

                "Region",

                "URL_Location",

                "Category",

                "URL_Category"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------

    print("\nCity Distribution:")

    print(
        df["City"]
        .value_counts()
    )

    print("\nState Distribution:")

    print(
        df["State"]
        .value_counts()
    )

    print("\nCountry Distribution:")

    print(
        df["Country"]
        .value_counts()
    )

    print("\nRegion Distribution:")

    print(
        df["Region"]
        .value_counts()
    )

    print("\nCategory Distribution:")

    print(
        df["Category"]
        .value_counts()
    )

    # --------------------------------------------------------
    # UNKNOWN COUNTS
    # --------------------------------------------------------

    print("\nUnknown Counts:")

    print(
        "Unknown City:",
        (df["City"] == "Unknown").sum()
    )

    print(
        "Unknown State:",
        (df["State"] == "Unknown").sum()
    )

    print(
        "Unknown Country:",
        (df["Country"] == "Unknown").sum()
    )

    print(
        "Unknown Region:",
        (df["Region"] == "Unknown").sum()
    )

    print(
        "Unknown Category:",
        (df["Category"] == "Unknown").sum()
    )

    # --------------------------------------------------------
    # OUTPUT FILE NAME
    # --------------------------------------------------------

    base_name = os.path.splitext(
        file_name
    )[0]

    output_file = (
        base_name
        + "_enriched.csv"
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        output_file
    )

    # --------------------------------------------------------
    # SAVE OUTPUT
    # --------------------------------------------------------

    df.to_csv(
        output_path,
        index=False
    )

    print("\nOutput saved:")

    print(output_path)

    print(
        "Final Shape:",
        df.shape
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "URL LOCATION & CATEGORY EXTRACTION SYSTEM"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # FIND ALL CSV FILES
    # --------------------------------------------------------

    csv_files = [

        file

        for file in os.listdir(
            RAW_FOLDER
        )

        if file.lower().endswith(".csv")
    ]

    print(
        "\nTotal CSV files found:",
        len(csv_files)
    )

    if not csv_files:

        print(
            "\nNo CSV files found in:"
        )

        print(
            RAW_FOLDER
        )

        return

    # --------------------------------------------------------
    # PROCESS EACH FILE SEPARATELY
    # --------------------------------------------------------

    for file_name in csv_files:

        process_file(
            file_name
        )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "ALL CSV FILES PROCESSED SUCCESSFULLY"
    )

    print("=" * 70)


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()