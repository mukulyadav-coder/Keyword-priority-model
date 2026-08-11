import re
import pandas as pd


def calculate_keyword_quality(keyword):

    if pd.isna(keyword):
        return 0

    keyword = str(keyword).strip().lower()

    if not keyword:
        return 0

    score = 100

    # Very short keyword
    if len(keyword) <= 2:
        score -= 50

    elif len(keyword) <= 3:
        score -= 30

    # Remove punctuation
    clean_keyword = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        keyword
    )

    words = clean_keyword.split()

    # Single character words
    if any(len(word) == 1 for word in words):
        score -= 25

    # Too many special characters
    special_chars = len(
        re.findall(
            r"[^a-zA-Z0-9\s]",
            keyword
        )
    )

    if special_chars >= 2:
        score -= 10

    # Extremely long keyword
    if len(words) > 10:
        score -= 10

    return max(0, min(100, score))


def add_keyword_quality(df):

    df["Keyword_Quality_Score"] = (
        df["Keyword"]
        .apply(calculate_keyword_quality)
    )

    return df