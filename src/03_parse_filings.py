# 03_parse_filings.ipynb

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Load the filings data
filings_data = pd.read_csv('../data/recent_filings.csv')

headers = {
    'User-Agent': 'Ahmet Besiroglu (abesiroglu@masterworks.com)'
}

def fetch_filing_text(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the file: {e}")
        return None

def parse_filing_text(text, cik, company_name, form, accession_number, filing_date):
    try:
        soup = BeautifulSoup(text, 'html.parser')
        return soup
    except Exception as e:
        print(f"html.parser failed for CIK {cik}, Company {company_name}, Form {form}, Accession {accession_number}, Date {filing_date}: {e}")
        try:
            soup = BeautifulSoup(text, 'lxml')
            return soup
        except Exception as e:
            print(f"lxml parser failed for CIK {cik}, Company {company_name}, Form {form}, Accession {accession_number}, Date {filing_date}: {e}")
            try:
                soup = BeautifulSoup(text, 'html5lib')
                return soup
            except Exception as e:
                print(f"html5lib parser failed for CIK {cik}, Company {company_name}, Form {form}, Accession {accession_number}, Date {filing_date}: {e}")
                return None

def find_section_link(soup, section_names):
    toc_entries = soup.find_all(['a', 'b', 'font'])
    for entry in toc_entries:
        entry_text = entry.get_text(strip=True).lower()
        for section_name in section_names:
            if section_name.lower() in entry_text:
                if entry.name == 'a' and 'href' in entry.attrs:
                    return entry
                elif entry.find('a') and 'href' in entry.find('a').attrs:
                    return entry.find('a')
    return None

def extract_tables(soup):
    statements = {
        "Consolidated Balance Sheet": ["Consolidated Balance Sheets", "Balance Sheet"],
        "Consolidated Statement of Operations": ["Consolidated Statements of Operations", "Statement of Operations"],
        "Consolidated Statement of Members’ Equity": ["Consolidated Statements of Members’ Equity", "Statement of Members’ Equity", "Statement of Member’s Equity"],
        "Consolidated Statement of Cash Flows": ["Consolidated Statements of Cash Flows", "Statement of Cash Flows"]
    }

    extracted_data = []

    if soup is None:
        return extracted_data

    for statement, variations in statements.items():
        link = find_section_link(soup, [statement] + variations)
        if link:
            section_id = link['href'].replace('#', '')
            section = soup.find('a', {'name': section_id})
            if section:
                table = section.find_next('table')
                while table:
                    if not any(keyword in table.get_text(strip=True).lower() for keyword in ["$", "shares"]):
                        table = table.find_next('table')
                        continue

                    rows = table.find_all('tr')
                    table_data = []
                    for row in rows:
                        cols = row.find_all('td')
                        col_data = [col.get_text(strip=True) for col in cols]
                        table_data.append(col_data)

                    extracted_data.append({
                        'Statement': statement,
                        'Data': table_data
                    })
                    break
    return extracted_data

# Function to remove unnecessary line breaks and spaces within cells
def clean_cell(cell):
    if isinstance(cell, str):
        # Replace line breaks and extra spaces with a single space
        return ' '.join(cell.split())
    return cell

# Create the main data directory
main_data_dir = '../data/entities'
os.makedirs(main_data_dir, exist_ok=True)

all_extracted_data = []
parsing_errors = []

for index, row in filings_data.iterrows():
    cik = row['CIK']
    company_name = row['Company Name']
    form = row['form']
    accession_number = row['accession_number']
    filing_date = row['filing_date']
    
    # Create directories for the entity, form type, and statements
    entity_dir = os.path.join(main_data_dir, company_name)
    form_dir = os.path.join(entity_dir, form)
    statements_dir = os.path.join(form_dir, 'statements')
    os.makedirs(statements_dir, exist_ok=True)
    
    txt_url = row['txt_file_url']
    filing_text = fetch_filing_text(txt_url)
    if filing_text:
        soup = parse_filing_text(filing_text, cik, company_name, form, accession_number, filing_date)
        if soup:
            tables = extract_tables(soup)
            for table in tables:
                statement_df = pd.DataFrame(table['Data'])
                statement_df_cleaned = statement_df.applymap(clean_cell)
                statement_type = table['Statement'].replace(' ', '_')
                file_name = f"{statement_type}.csv"
                file_path = os.path.join(statements_dir, file_name)
                statement_df_cleaned.to_csv(file_path, index=False, header=False)
                all_extracted_data.append({
                    'CIK': cik,
                    'Company Name': company_name,
                    'Form': form,
                    'Accession Number': accession_number,
                    'Filing Date': filing_date,
                    'Statement': table['Statement'],
                    'File': file_path
                })
        else:
            parsing_errors.append({
                'CIK': cik,
                'Company Name': company_name,
                'Form': form,
                'Accession Number': accession_number,
                'Filing Date': filing_date
            })

# Optionally, save the metadata to a file for reference
metadata_file_path = os.path.join(main_data_dir, 'extracted_filing_data_metadata.json')
with open(metadata_file_path, 'w') as f:
    json.dump(all_extracted_data, f, indent=4)

# Save parsing errors to a separate file
parsing_errors_file_path = os.path.join(main_data_dir, 'parsing_errors.json')
with open(parsing_errors_file_path, 'w') as f:
    json.dump(parsing_errors, f, indent=4)

print(f"Extracted filing data has been saved to individual CSV files and metadata to '{metadata_file_path}'")
print(f"Parsing errors have been saved to '{parsing_errors_file_path}'")
