import pandas as pd
import os
import json
import glob
from envs.env import json_path, output_path


# Directory containing the Excel files
excel_dir = output_path + "excel/"

# Directory to save JSON files
json_dir = output_path + "excel_to_json/"
os.makedirs(json_dir, exist_ok=True)

# Fetch all .xlsx files from the directory
excel_files = glob.glob(os.path.join(excel_dir, "*.xlsx"))


# Function to process each sheet and save as JSON
def process_sheet(df, json_dir):
    # Drop rows with NaN in the 'name' column
    df = df.dropna(subset=["name"])

    # Convert columns to appropriate data types
    df["rule_id"] = df["rule_id"].astype(int)
    df["weight"] = df["weight"].astype(float)
    for col in ["name", "description"]:
        df[col] = df[col].astype(str)

    # Aggregate all data in 'samples' and 'signatures' columns
    df["samples"] = df["samples"].str.split().sum()
    df["signatures"] = df["signatures"].str.split().sum()

    # Keep unique values only
    df["samples"] = list(set(df["samples"]))
    df["signatures"] = list(set(df["signatures"]))

    # Convert dataframe to JSON format
    json_data = df.iloc[0].to_json()

    # Save to JSON file using 'name' value
    json_filename = df["name"].iloc[0] + ".json"
    json_filepath = os.path.join(json_dir, json_filename)
    with open(json_filepath, "w") as json_file:
        json_file.write(json_data)


# Process each Excel file
for excel_file in excel_files:
    # Read all sheets into a dictionary of dataframes
    all_sheets = pd.read_excel(
        excel_file, sheet_name=None, dtype={"rule_id": "Int64", "weight": "float"}
    )

    # Process each sheet in the dictionary
    for sheet_name, df in all_sheets.items():
        process_sheet(df, json_dir)

print("All sheets have been converted to JSON files.")
