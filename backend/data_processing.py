import pandas as pd


def load_data(file_path):

    print("\n======================================")
    print("Loading Dataset")
    print("======================================")

    print("File:", file_path)

    try:

        df = pd.read_csv(
            file_path,
            encoding="latin1"
        )

        print("Dataset loaded successfully!")
        print("Shape:", df.shape)

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nFirst 5 rows:")
        print(df.head())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        return df

    except Exception as e:

        print("\nError while loading dataset:")
        print(e)

        return None


def clean_data(df):

    print("\nCleaning data...")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing values
    df = df.fillna(0)

    print("Data cleaning completed!")

    return df