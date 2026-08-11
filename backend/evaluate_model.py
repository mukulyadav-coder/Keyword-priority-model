import pandas as pd


# ==========================================
# Load Prediction Output
# ==========================================

df = pd.read_csv(
    "data/output/predictions.csv"
)


# ==========================================
# Basic Model Statistics
# ==========================================

print("\n===== MODEL EVALUATION =====\n")

print("Total Keywords:", len(df))

print(
    "Average Priority Score:",
    round(df["Priority_Score"].mean(), 2)
)

print(
    "Minimum Priority Score:",
    df["Priority_Score"].min()
)

print(
    "Maximum Priority Score:",
    df["Priority_Score"].max()
)


# ==========================================
# Priority Distribution
# ==========================================

print("\n===== PRIORITY DISTRIBUTION =====\n")

distribution = (
    df["Priority_Category"]
    .value_counts()
    .sort_index()
)

print(distribution)


# ==========================================
# Average Features by Priority
# ==========================================

print("\n===== AVERAGE FEATURES BY PRIORITY =====\n")

summary = (
    df.groupby("Priority_Category")
    .agg(
        Keyword_Count=("Keyword", "count"),
        Avg_Volume=("Volume", "mean"),
        Avg_Visits=("Estimated Visits", "mean"),
        Avg_Position=("Position", "mean"),
        Avg_CPC=("CPC", "mean"),
        Avg_SEO_Difficulty=("SEO Difficulty", "mean"),
        Avg_Priority_Score=("Priority_Score", "mean")
    )
    .round(2)
)

print(summary)


# ==========================================
# Top 20 Keywords
# ==========================================

print("\n===== TOP 20 KEYWORDS =====\n")

top_keywords = df[
    [
        "Keyword",
        "Volume",
        "Position",
        "Estimated Visits",
        "CPC",
        "Priority_Score",
        "Priority_Category",
        "Priority_Rank"
    ]
].head(20)

print(
    top_keywords.to_string(index=False)
)


print("\n===== EVALUATION COMPLETED =====")