import pandas as pd
from keyword_quality import add_keyword_quality


def prepare_features(df):

    # ==========================================
    # 1. CPC Cleaning
    # ==========================================

    df["CPC"] = (
        df["CPC"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["CPC"] = pd.to_numeric(
        df["CPC"],
        errors="coerce"
    )

    df["CPC"] = df["CPC"].fillna(0)


    # ==========================================
    # 2. Volume Score
    # ==========================================

    df["Volume_Score"] = (
        df["Volume"]
        .rank(pct=True)
        * 100
    )


    # ==========================================
    # 3. Estimated Visits Score
    # ==========================================

    df["Visits_Score"] = (
        df["Estimated Visits"]
        .rank(pct=True)
        * 100
    )


    # ==========================================
    # 4. Position Score
    # ==========================================
    # Lower position = better

    df["Position_Score"] = (
        1 - df["Position"].rank(pct=True)
    ) * 100


    # ==========================================
    # 5. CPC Score
    # ==========================================

    df["CPC_Score"] = (
        df["CPC"]
        .rank(pct=True)
        * 100
    )


    # ==========================================
    # 6. SEO Difficulty
    # ==========================================
    # Lower difficulty = better opportunity

    df["SEO_Opportunity"] = (
        1 - df["SEO Difficulty"].rank(pct=True)
    ) * 100


    # ==========================================
    # 7. Paid Difficulty
    # ==========================================
    # Lower difficulty = better opportunity

    df["Paid_Opportunity"] = (
        1 - df["Paid Difficulty"].rank(pct=True)
    ) * 100
    df = add_keyword_quality(df)


    return df