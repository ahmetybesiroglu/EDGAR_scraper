import requests
import json
import pandas as pd
import os

# Ensure data directory exists
os.makedirs('../data', exist_ok=True)

# Load the CIK list and ensure leading zeros
cik_df = pd.read_csv('../data/masterworks_entity_list.csv')
cik_df['CIK'] = cik_df['CIK'].astype(str).str.zfill(10)

# Load the active SPV entities list
active_spv_df = pd.read_csv('../data/active_spv_entities.csv')

# Filter the CIK list based on active SPV entities
filtered_cik_df = cik_df[cik_df['Company Name'].str.upper().isin(active_spv_df['Entity'].str.upper())]

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

            # Filter for the most recent 1-K and 1-SA filings
            latest_filings = {'1-K': None, '1-SA': None}
            for form, accession_number, filing_date, primary_document in zip(forms, accession_numbers, filing_dates, primary_documents):
                if form in latest_filings:
                    if latest_filings[form] is None or filing_date > latest_filings[form]['filing_date']:
                        latest_filings[form] = {
                            'CIK': cik,
                            'Company Name': company_name,
                            'form': form,
                            'accession_number': accession_number,
                            'filing_date': filing_date,
                            'primary_document': primary_document,
                            'document_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{primary_document}",
                            'txt_file_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{accession_number}.txt"
                        }
            for filing in latest_filings.values():
                if filing:
                    all_filings_data.append(filing)
    else:
        print(f"Failed to download data for CIK {cik}. Status code: {response.status_code}")

# Save all filings data to a DataFrame
df_filings = pd.DataFrame(all_filings_data)

# Save the filtered filings data to a CSV file
output_path = '../data/recent_filings.csv'
df_filings.to_csv(output_path, index=False)
print(f"Most recent filings data has been written to '{output_path}'")
