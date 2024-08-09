import requests
import json
import pandas as pd
import os
from fuzzywuzzy import process
from datetime import datetime

# Ensure data directory exists
os.makedirs('../data', exist_ok=True)

# Load the CIK list and ensure leading zeros
cik_df = pd.read_csv('../data/masterworks_entity_list.csv')
cik_df['CIK'] = cik_df['CIK'].astype(str).str.zfill(10)

# Load the active SPV entities list
active_spv_df = pd.read_csv('../data/active_spv_entities.csv')

# Filter settings
FORM_TYPES = ['1-K', '1-SA']  # List of form types to include
MAX_RECENT_FILINGS = 1        # Number of most recent filings to fetch per entity
DATE_RANGE = ('2023-01-01', '2024-06-31')  # Date range filter as (start_date, end_date)

# Convert date range strings to datetime objects
start_date, end_date = [datetime.strptime(date, '%Y-%m-%d') for date in DATE_RANGE]

try:
    # Prepare the lists for fuzzy matching
    active_spv_entities = active_spv_df['Entity'].str.upper().tolist()
    company_names = cik_df['Company Name'].str.upper().tolist()

    # Use fuzzy matching to find the best matches
    matches = []
    for entity in active_spv_entities:
        match, score = process.extractOne(entity, company_names)
        if score > 80:  # Adjust the threshold as needed
            matches.append(match)

    # Filter the CIK list based on fuzzy matching results
    filtered_cik_df = cik_df[cik_df['Company Name'].str.upper().isin(matches)]
except Exception as e:
    print(f"Fuzzy matching failed with error: {e}")
    print("Falling back to simple lowercase and capitalize matching.")

    # Simple lowercase and capitalize matching
    active_spv_entities = active_spv_df['Entity'].str.lower().str.title().tolist()
    cik_df['Company Name'] = cik_df['Company Name'].str.lower().str.title()
    filtered_cik_df = cik_df[cik_df['Company Name'].isin(active_spv_entities)]

headers = {
    'User-Agent': 'Ahmet Besiroglu (abesiroglu@masterworks.com)'
}

all_filings_data = []

for _, row in filtered_cik_df.iterrows():
    cik = row['CIK']
    company_name = row['Company Name']
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        submission_history = response.json()
        recent_filings = submission_history.get('filings', {}).get('recent', {})
        if isinstance(recent_filings, dict):
            forms = recent_filings.get('form', [])
            accession_numbers = recent_filings.get('accessionNumber', [])
            filing_dates = recent_filings.get('filingDate', [])
            primary_documents = recent_filings.get('primaryDocument', [])

            latest_filings = {}
            for form, accession_number, filing_date, primary_document in zip(forms, accession_numbers, filing_dates, primary_documents):
                if form in FORM_TYPES:
                    filing_date_obj = datetime.strptime(filing_date, '%Y-%m-%d')
                    if start_date <= filing_date_obj <= end_date:
                        if form not in latest_filings:
                            latest_filings[form] = []
                        latest_filings[form].append({
                            'CIK': cik,
                            'Company Name': company_name,
                            'form': form,
                            'accession_number': accession_number,
                            'filing_date': filing_date,
                            'primary_document': primary_document,
                            'document_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{primary_document}",
                            'txt_file_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{accession_number}.txt"
                        })

            for form, filings in latest_filings.items():
                # Sort filings by date and take the most recent ones based on the limit
                filings_sorted = sorted(filings, key=lambda x: x['filing_date'], reverse=True)
                all_filings_data.extend(filings_sorted[:MAX_RECENT_FILINGS])
    else:
        print(f"Failed to download data for CIK {cik}. Status code: {response.status_code}")

# Save all filings data to a CSV file
df_filings = pd.DataFrame(all_filings_data)
print(df_filings)

output_path = '../data/recent_filings.csv'
df_filings.to_csv(output_path, index=False)
print(f"Most recent filings data has been written to '{output_path}'")
