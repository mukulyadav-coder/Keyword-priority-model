def calculate_priority_score(df):

    # ==========================================
    # Calculate Final Priority Score
    # ==========================================

    df["Priority_Score"] = (
        df["Volume_Score"] * 0.22
        + df["Visits_Score"] * 0.18
        + df["Position_Score"] * 0.18
        + df["CPC_Score"] * 0.12
        + df["SEO_Opportunity"] * 0.10
        + df["Paid_Opportunity"] * 0.10
        + df["Keyword_Quality_Score"] * 0.10
    )

    # Keep score between 0 and 100
    df["Priority_Score"] = (
        df["Priority_Score"]
        .clip(0, 100)
        .round(2)
    )

    return df


def assign_priority_category(df):

    # ==========================================
    # Assign Priority Category
    # ==========================================

    def get_category(score):

        if score >= 80:
            return "P1 - Critical"

        elif score >= 60:
            return "P2 - High"

        elif score >= 40:
            return "P3 - Medium"

        elif score >= 20:
            return "P4 - Low"

        else:
            return "P5 - Very Low"

    df["Priority_Category"] = (
        df["Priority_Score"]
        .apply(get_category)
    )

    return df


def assign_priority_rank(df):

    # ==========================================
    # Assign Priority Rank
    # ==========================================

    # Handle missing and infinite scores
    df["Priority_Score"] = (
        df["Priority_Score"]
        .replace([float("inf"), float("-inf")], 0)
        .fillna(0)
    )

    # Calculate rank
    df["Priority_Rank"] = (
        df["Priority_Score"]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    return df