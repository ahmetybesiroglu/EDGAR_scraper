# 01_scrape_edgar.ipynb

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

# Create data directory if it doesn't exist
os.makedirs('../data', exist_ok=True)

# Initialize the WebDriver
driver = webdriver.Chrome()

# Define the base URL for the main page
base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=masterworks&owner=include&match=&start={}&count=40&hidefilings=0"

# Function to scrape links to individual company pages from the first page
def get_company_links(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//table[@class="tableFile2"]/tbody/tr'))
    )
    rows = driver.find_elements(By.XPATH, '//table[@class="tableFile2"]/tbody/tr')
    company_links = []
    for row in rows[1:]:  # skip the header row
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) >= 2:
            cik_element = cols[0].find_element(By.TAG_NAME, 'a')
            company_cik = cik_element.text
            company_url = cik_element.get_attribute('href')
            company_name = cols[1].text.split("\n")[0]
            if "masterworks" in str.lower(company_name):  # filter based on the presence of "Masterworks" in the company name
                company_links.append((company_cik, company_name))
    return company_links

# Initialize a list to hold all the scraped data
all_data = []

# Start scraping from the main page and handle pagination through URL
start = 0
while True:
    driver.get(base_url.format(start))
    try:
        company_links = get_company_links(driver)
    except Exception as e:
        print(f"No more companies: {e}")
        break
    
    if not company_links:
        break
    
    all_data.extend(company_links)

    start += 40

# Close the WebDriver
driver.quit()

# Convert the scraped data into a DataFrame
df = pd.DataFrame(all_data, columns=['CIK', 'Company Name'])

# Add a space after each comma in the 'Company Name' column
df['Company Name'] = df['Company Name'].apply(lambda x: ', '.join([name.strip() for name in x.split(',')]))

# Print the scraped data
print(df)

# Ensure CIK column is saved as text to preserve leading zeros
df['CIK'] = df['CIK'].astype(str)

print(df)

# Ensure data directory exists
os.makedirs('../data', exist_ok=True)

# Save the data to a CSV file
output_path = '../data/masterworks_entity_list.csv'
df.to_csv(output_path, index=False)

print(f"Data scraping complete. All data has been saved to '{output_path}'.")
