import os
import pandas as pd

from feature_engineering import prepare_features

from scoring import (
    calculate_priority_score,
    assign_priority_category,
    assign_priority_rank
)


# =========================================================
# FOLDER PATHS
# =========================================================

input_folder = "data/raw"
output_folder = "data/output"


# =========================================================
# CREATE OUTPUT FOLDER
# =========================================================

os.makedirs(output_folder, exist_ok=True)


# =========================================================
# FIND ALL CSV FILES
# =========================================================

files = [
    file
    for file in os.listdir(input_folder)
    if file.lower().endswith(".csv")
]


if len(files) == 0:

    print("No CSV files found in:", input_folder)

else:

    print("========================================")
    print("KEYWORD PRIORITY MODEL")
    print("========================================")

    print("Total CSV files found:", len(files))


    # =====================================================
    # PROCESS EACH FILE
    # =====================================================

    for file_name in files:

        print("\n========================================")
        print("Processing:", file_name)
        print("========================================")


        # -------------------------------------------------
        # INPUT FILE PATH
        # -------------------------------------------------

        file_path = os.path.join(
            input_folder,
            file_name
        )


        # -------------------------------------------------
        # LOAD DATA
        # -------------------------------------------------

        try:

            df = pd.read_csv(
                file_path,
                encoding="latin1"
            )

        except Exception as e:

            print("Error loading file:", e)

            continue


        print("Dataset loaded successfully!")

        print(
            "Original Shape:",
            df.shape
        )


        # -------------------------------------------------
        # FEATURE ENGINEERING
        # -------------------------------------------------

        df = prepare_features(df)

        print("Feature engineering completed!")


        # -------------------------------------------------
        # PRIORITY SCORE
        # -------------------------------------------------

        df = calculate_priority_score(df)

        print("Priority score calculated!")


        # -------------------------------------------------
        # PRIORITY CATEGORY
        # -------------------------------------------------

        df = assign_priority_category(df)

        print("Priority categories assigned!")


        # -------------------------------------------------
        # PRIORITY RANK
        # -------------------------------------------------

        df = assign_priority_rank(df)

        print("Priority ranking completed!")


        # -------------------------------------------------
        # SORT BY PRIORITY SCORE
        # -------------------------------------------------

        df = df.sort_values(
            by="Priority_Score",
            ascending=False
        )


        # -------------------------------------------------
        # OUTPUT FILE NAME
        # -------------------------------------------------

        file_without_extension = os.path.splitext(
            file_name
        )[0]


        output_file_name = (
            file_without_extension
            + "_predictions.csv"
        )


        output_file = os.path.join(
            output_folder,
            output_file_name
        )


        # -------------------------------------------------
        # SAVE PREDICTION
        # -------------------------------------------------

        df.to_csv(
            output_file,
            index=False
        )


        # -------------------------------------------------
        # DISPLAY TOP 20
        # -------------------------------------------------

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


        # -------------------------------------------------
        # OUTPUT MESSAGE
        # -------------------------------------------------

        print("\n--------------------------------")
        print("Priority model completed!")
        print("--------------------------------")

        print(
            "Output saved at:",
            output_file
        )


        # -------------------------------------------------
        # CATEGORY DISTRIBUTION
        # -------------------------------------------------

        print("\nPriority Category Distribution:")

        print(
            df["Priority_Category"]
            .value_counts()
            .sort_index()
        )


        # -------------------------------------------------
        # SCORE STATISTICS
        # -------------------------------------------------

        print("\nPriority Score Statistics:")

        print(
            df["Priority_Score"].describe()
        )


        # -------------------------------------------------
        # PRIORITY SUMMARY
        # -------------------------------------------------

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


    # =====================================================
    # ALL FILES COMPLETED
    # =====================================================

    print("\n\n========================================")
    print("ALL FILES PROCESSED SUCCESSFULLY!")
    print("========================================")