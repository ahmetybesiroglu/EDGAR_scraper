
# EDGAR Data Scraper

This project is designed to scrape and process data from the SEC's EDGAR database. The primary focus is on extracting financial information from Masterworks entities' filings.

## Project Structure

```
project-root/
│
├── data/
│   └── (your data files)
│
├── src/
│   ├── 01_scrape_edgar.py
│   ├── 02_fetch_recent_filings.py
│   ├── 03_parse_filings.py
│   └── 04_extract_values.py
│
├── README.md
├── .gitignore
├── config.json
└── requirements.txt
```

## Scripts

- **01_scrape_edgar.py**: Scrapes the EDGAR database for Masterworks entities.
- **02_fetch_recent_filings.py**: Fetches the most recent filings for the scraped entities.
- **03_parse_filings.py**: Parses the filings to extract relevant data.
- **04_extract_values.py**: Extracts specific financial values from the filings and structures the data for analysis.

## Configuration

- **config.json**: Configuration file specifying the lines to extract from financial statements.

## Data

- **data/**: Directory to store the scraped and processed data files.

## Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine using the following command:

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies. You can set up a virtual environment using `venv`:

```bash
python3 -m venv venv
```

This command creates a virtual environment in a directory named `venv`.

### 3. Activate the Virtual Environment

- On **Windows**:

    ```bash
    venv\Scripts\Activate
    ```

- On **macOS/Linux**:

    ```bash
    source venv/bin/activate
    ```

Once the virtual environment is activated, you'll see the environment's name in your terminal prompt.

### 4. Install the Required Packages

After activating your virtual environment, install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command installs all the dependencies listed in the `requirements.txt` file.

### 5. Running the Scripts

Run the scripts in the following order:

1. **01_scrape_edgar.py**: This script scrapes the EDGAR database for Masterworks entities.
   ```bash
   python src/01_scrape_edgar.py
   ```

2. **02_fetch_recent_filings.py**: This script fetches the most recent filings for the entities scraped in the first step.
   ```bash
   python src/02_fetch_recent_filings.py
   ```

3. **03_parse_filings.py**: This script parses the filings to extract relevant data.
   ```bash
   python src/03_parse_filings.py
   ```

4. **04_extract_values.py**: This script extracts specific financial values from the filings and structures the data for analysis.
   ```bash
   python src/04_extract_values.py
   ```

### 6. Deactivating the Virtual Environment

When you're done, you can deactivate the virtual environment with the following command:

```bash
deactivate
```

## Contributing

Please fork the repository and submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
