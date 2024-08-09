import os
import pandas as pd
import json

# Define the directory containing the data
data_dir = '../data/entities'

# Ensure the data directory exists
os.makedirs(data_dir, exist_ok=True)

# Load the JSON configuration
config_path = '../config.json'
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Function to handle potential negative values
def handle_negative_value(value):
    if isinstance(value, str) and value.startswith('('):
        return '-' + value.strip('(').rstrip(')')
    return value

# Function to extract the required value from the specified column
def extract_value(df, line_name, column_idx, occurrence=0, entity_name='', form_type=''):
    try:
        matching_rows = [row for i, row in df.iterrows() if line_name in row.to_string()]
        print(f"Entity: {entity_name}, Form: {form_type}, Line: '{line_name}'")
        print(f"Matching rows for '{line_name}': {matching_rows}")
        if not matching_rows:
            return 0

        row = matching_rows[occurrence]
        value = row.iloc[column_idx]
        print(f"Extracted value before handling negative for '{line_name}': {value}")
        return handle_negative_value(value)
    except Exception as e:
        print(f"Error extracting value for '{line_name}' in Entity '{entity_name}', Form '{form_type}': {e}")
        return 0

# Initialize an empty dictionary to store the extracted data in a pivot format
data_dict = {}

# Walk through the data directory to find the relevant files
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith('.csv'):
            entity_name = os.path.basename(os.path.dirname(os.path.dirname(root)))
            form_type = os.path.basename(os.path.dirname(root))

            print(f"Processing Entity: {entity_name}, Form: {form_type}, File: {file}")

            # Check if the form type exists in the config
            if form_type in config and file in config[form_type]:
                file_path = os.path.join(root, file)
                df = pd.read_csv(file_path)

                for item in config[form_type][file]:
                    line_name = item["line_name"]
                    column_name = item["column_name"]
                    extract_method = item["extract_method"]

                    if extract_method == "extract_value":
                        column_idx = item.get("column_idx", 0)
                        occurrence = item.get("occurrence", 0)
                        value = extract_value(df, line_name, column_idx, occurrence, entity_name, form_type)

                    if column_name not in data_dict:
                        data_dict[column_name] = {}
                    data_dict[column_name][entity_name] = value
                    print(f"Extracted data for '{column_name}': {value}")

# Convert the dictionary to a DataFrame
df_all_values = pd.DataFrame(data_dict).T

# Ensure rows are ordered as per the JSON config
row_order = [item["column_name"] for item in config["1-SA"]["Consolidated_Statement_of_Cash_Flows.csv"]]
df_all_values = df_all_values.reindex(row_order)

# Ensure columns are ordered by entity name
column_order = sorted(df_all_values.columns)
df_all_values = df_all_values[column_order]

# Print the DataFrame to check the extracted values
print(df_all_values)

# Determine the output file path based on form type
output_file_path = '../data/1-SA_extracted_data.csv'
df_all_values.to_csv(output_file_path)

print(f"Extracted data has been saved to '{output_file_path}'")
