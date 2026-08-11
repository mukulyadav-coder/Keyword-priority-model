import pandas as pd

from feature_engineering import prepare_features

from scoring import (
    calculate_priority_score,
    assign_priority_category,
    assign_priority_rank
)


file_path = "data/raw/zomato_keywords.csv"

df = pd.read_csv(
    file_path,
    encoding="latin1"
)

print("Dataset loaded successfully!")

print(
    "Original Shape:",
    df.shape
)


df = prepare_features(df)

print("Feature engineering completed!")


df = calculate_priority_score(df)

print("Priority score calculated!")


df = assign_priority_category(df)

print("Priority categories assigned!")


df = assign_priority_rank(df)

print("Priority ranking completed!")


df = df.sort_values(
    by="Priority_Score",
    ascending=False
)


columns_to_show = [
    "Keyword",
    "Volume",
    "Position",
    "Estimated Visits",
    "CPC",
    "SEO Difficulty",
    "Paid Difficulty",
    "Priority_Score",
    "Priority_Category",
    "Priority_Rank"
]


print("\nTop 20 Priority Keywords:\n")

print(
    df[columns_to_show]
    .head(20)
    .to_string(index=False)
)


output_file = "data/output/predictions.csv"

df.to_csv(
    output_file,
    index=False
)


print("\n--------------------------------")
print("Priority model completed!")
print("--------------------------------")

print(
    "Output saved at:",
    output_file
)


print("\nPriority Category Distribution:")

print(
    df["Priority_Category"]
    .value_counts()
    .sort_index()
)


print("\nPriority Score Statistics:")

print(
    df["Priority_Score"].describe()
)
print("\nPriority Summary:")

summary = (
    df.groupby("Priority_Category")
    .agg(
        Keyword_Count=("Keyword", "count"),
        Average_Score=("Priority_Score", "mean"),
        Average_Volume=("Volume", "mean"),
        Average_Position=("Position", "mean"),
        Average_Visits=("Estimated Visits", "mean")
    )
    .round(2)
)

print(summary)