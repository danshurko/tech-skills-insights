# tech-skills-insights

This project collects job listings from [djinni.co](https://djinni.co), extracts all relevant information for future analysis, and uses the OpenAI API to extract keywords from job descriptions.

## Current Features

- Scrapes job listings from [djinni.co](https://djinni.co)
- Saves (example):
  - Job title
  - Description
  - Salary (if available)
  - Tech stack / tags
  - Job URL
- Extracts relevant keywords from each job description using OpenAI's GPT model

## Project Structure

- `data_parser.py` — collects job data and uploads it to AWS S3 in Parquet format
- `extract_keywords.py` — extracts keywords and stores them in JSON format on S3

## Data Storage

- Job listings are saved in `.parquet` format
- Extracted keywords are saved in `.json` format
- All files are stored in a specified AWS S3 bucket
- Example data structure:
  ```
  s3://bucket-name/
    ├── djinni/
    │   └── date=2025-03-05/
    │       ├── eb7c1249ffe1403293d74ab478b6f39d-0.parquet
    │       └── keywords.json
  ```

> You can check the `attachments/screenshots` folder for example outputs.

## Planned Features

- Analyze collected job data:
  - Most frequent keywords and technologies
  - Salary distribution and correlations
  - Tech trends over time
- Job categorization by domain (e.g. Web, Mobile, GameDev, Data Science)
- Visual dashboards using Streamlit or Dash
- Recommendation tools (e.g. "which skills to learn")
- Extend scraping to other job platforms

## Potential Directions for Data Analysis

- Clustering jobs using NLP and ML
- Skill gap analysis
- Market demand forecast
- Salary prediction models
- Geo-based analysis (if location data becomes available)

## Usage

1. **Scrape jobs**:
   ```bash
   python data_parser.py
   ```

2. **Extract keywords** (requires OpenAI API key):
   ```bash
   python extract_keywords.py
   ```

3. Output files will be automatically saved to your configured S3 bucket.

## Requirements

- Python 3.9+
- AWS credentials configured (`boto3`)
- OpenAI API key
- Libraries:
  - `requests`, `beautifulsoup4`, `pandas`, `pyarrow`, `openai`, `boto3`, `s3fs`,  `emoji`

## Technologies Used

- Python 3
- Web scraping: `requests`, `BeautifulSoup`
- Keyword extraction: `OpenAI GPT API`
- Data processing: `pandas`, `pyarrow`
- Storage: `AWS S3`

---

> Project is in early development. Focus is on collecting clean, structured data. Analytical tools are coming soon.
