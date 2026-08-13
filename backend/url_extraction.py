import pandas as pd
import os
from urllib.parse import urlparse


# ============================================================
# FOLDERS
# ============================================================

RAW_FOLDER = "data/raw"
OUTPUT_FOLDER = "data/processed"

URL_COLUMN = "Ranking URL"


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# LOCATION REFERENCE
# ============================================================

LOCATION_DATA = {

    "mumbai": {
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India"
    },

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

    "chennai": {
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India"
    },

    "kolkata": {
        "city": "Kolkata",
        "state": "West Bengal",
        "country": "India"
    },

    "hyderabad": {
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India"
    },

    "pune": {
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India"
    },

    "jaipur": {
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India"
    },

    "ahmedabad": {
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India"
    },

    "lucknow": {
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "country": "India"
    },

    "chandigarh": {
        "city": "Chandigarh",
        "state": "Chandigarh",
        "country": "India"
    },

    "indore": {
        "city": "Indore",
        "state": "Madhya Pradesh",
        "country": "India"
    },

    "surat": {
        "city": "Surat",
        "state": "Gujarat",
        "country": "India"
    },

    "nagpur": {
        "city": "Nagpur",
        "state": "Maharashtra",
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

    "patna": {
        "city": "Patna",
        "state": "Bihar",
        "country": "India"
    },

    "goa": {
        "city": "Goa",
        "state": "Goa",
        "country": "India"
    },

    "kochi": {
        "city": "Kochi",
        "state": "Kerala",
        "country": "India"
    },

    "dehradun": {
        "city": "Dehradun",
        "state": "Uttarakhand",
        "country": "India"
    }
}


# ============================================================
# CATEGORY REFERENCE
# ============================================================

CATEGORY_DATA = {

    "restaurants": "Restaurant",
    "restaurant": "Restaurant",

    "restaurants-near-me": "Restaurant",
    "restaurant-near-me": "Restaurant",

    "cafes": "Cafe",
    "cafe": "Cafe",

    "cafes-near-me": "Cafe",

    "bars": "Bar",
    "bar": "Bar",

    "bars-near-me": "Bar",

    "bakeries": "Bakery",
    "bakery": "Bakery",

    "bakeries-near-me": "Bakery",

    "pizza": "Pizza",

    "coffee": "Coffee",

    "hotels": "Hotel",
    "hotel": "Hotel",

    "desserts": "Dessert",
    "dessert": "Dessert",

    "sweet-shop": "Sweet Shop",

    "ice-cream": "Ice Cream",

    "fast-food": "Fast Food"
}


# ============================================================
# GET URL PARTS
# ============================================================

def get_url_parts(url):

    if pd.isna(url):
        return []

    url = str(url).strip().lower()

    if not url:
        return []

    try:

        parsed_url = urlparse(url)

        path = parsed_url.path.strip("/")

        if not path:
            return []

        return [
            part
            for part in path.split("/")
            if part
        ]

    except Exception:

        return []


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(url):

    parts = get_url_parts(url)

    result = {
        "City": "Unknown",
        "State": "Unknown",
        "Country": "Unknown"
    }

    if not parts:
        return result

    # --------------------------------------------------------
    # Check every URL part for known location
    # --------------------------------------------------------

    for part in parts:

        if part in LOCATION_DATA:

            location = LOCATION_DATA[part]

            result["City"] = location["city"]
            result["State"] = location["state"]
            result["Country"] = location["country"]

            return result

    return result


# ============================================================
# EXTRACT CATEGORY
# ============================================================

def extract_category(url):

    parts = get_url_parts(url)

    if not parts:
        return "Unknown"

    full_path = "/".join(parts)

    # --------------------------------------------------------
    # Exact category matching
    # --------------------------------------------------------

    for pattern, category in CATEGORY_DATA.items():

        if pattern in full_path:

            return category

    return "Unknown"


# ============================================================
# PROCESS ONE FILE
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
    # LOAD CSV
    # --------------------------------------------------------

    df = pd.read_csv(
        input_path,
        encoding="latin1"
    )

    print(
        "Original Shape:",
        df.shape
    )

    # --------------------------------------------------------
    # CHECK URL COLUMN
    # --------------------------------------------------------

    if URL_COLUMN not in df.columns:

        print(
            "ERROR: Ranking URL column not found."
        )

        print(
            "Available columns:",
            df.columns.tolist()
        )

        return

    # --------------------------------------------------------
    # EXTRACT LOCATION
    # --------------------------------------------------------

    location_data = (
        df[URL_COLUMN]
        .apply(extract_location)
    )

    location_df = pd.DataFrame(
        location_data.tolist()
    )

    # --------------------------------------------------------
    # EXTRACT CATEGORY
    # --------------------------------------------------------

    df["Category"] = (
        df[URL_COLUMN]
        .apply(extract_category)
    )

    # --------------------------------------------------------
    # ADD LOCATION COLUMNS
    # --------------------------------------------------------

    df["City"] = location_df["City"]

    df["State"] = location_df["State"]

    df["Country"] = location_df["Country"]

    # --------------------------------------------------------
    # REORDER COLUMNS
    # --------------------------------------------------------

    original_columns = [
        column
        for column in df.columns
        if column not in [
            "City",
            "State",
            "Country",
            "Category"
        ]
    ]

    df = df[
        original_columns
        + [
            "City",
            "State",
            "Country",
            "Category"
        ]
    ]

    # --------------------------------------------------------
    # SHOW SAMPLE
    # --------------------------------------------------------

    print("\nSample Result:")

    print(
        df[
            [
                URL_COLUMN,
                "City",
                "State",
                "Country",
                "Category"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\nCity Distribution:")

    print(
        df["City"].value_counts()
    )

    print("\nState Distribution:")

    print(
        df["State"].value_counts()
    )

    print("\nCategory Distribution:")

    print(
        df["Category"].value_counts()
    )

    # --------------------------------------------------------
    # OUTPUT FILE
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
    # SAVE
    # --------------------------------------------------------

    df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nOutput saved:",
        output_path
    )

    print(
        "Final Shape:",
        df.shape
    )


# ============================================================
# MAIN
# ============================================================

def main():

    csv_files = [
        file
        for file in os.listdir(RAW_FOLDER)
        if file.lower().endswith(".csv")
    ]

    print("=" * 70)
    print("URL LOCATION & CATEGORY EXTRACTION")
    print("=" * 70)

    print(
        "Total CSV files found:",
        len(csv_files)
    )

    if not csv_files:

        print(
            "No CSV files found."
        )

        return

    # --------------------------------------------------------
    # PROCESS EACH CSV SEPARATELY
    # --------------------------------------------------------

    for file_name in csv_files:

        process_file(file_name)

    print("\n" + "=" * 70)
    print("ALL FILES COMPLETED")
    print("=" * 70)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()