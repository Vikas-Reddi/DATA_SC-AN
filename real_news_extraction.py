import requests
import pandas as pd
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
from goose3 import Goose
import os

# Define the years and months to scrape
years = ["2023"]
months = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

# Unique to Economic Times archive, set initial start time
start_time_counter = 44927
urls_clo = set()  # Set to track unique URLs across iterations

# Define the day ranges for each month
days_in_month = {
    "1": range(1, 32), "2": range(1, 29), "3": range(1, 32), "4": range(1, 31),
    "5": range(1, 32), "6": range(1, 31), "7": range(1, 32), "8": range(1, 32),
    "9": range(1, 31), "10": range(1, 32), "11": range(1, 31), "12": range(1, 32)
}

# CSV file path to store the data
csv_file = 'EconomicTimes_Archive.csv'
csv_exists = os.path.isfile(csv_file)  # Check if CSV already exists to avoid repeated headers

# Function to fetch and parse the article content
def fetch_article_content(url):
    g = Goose()
    article = g.extract(url=url)
    title = article.title
    text = article.cleaned_text
    domain = article.domain
    source = re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))', domain)
    return title, text, source[0] if source else 'Unknown'

# Main loop for year, month, and day
for year in years:
    for month in months:
        for day in days_in_month[month]:
            archive_url = f'https://economictimes.indiatimes.com/archivelist/year-{year},month-{month},starttime-{start_time_counter}.cms'
            response = requests.get(archive_url)
            
            # Determine encoding and parse content
            encoding = response.encoding or EncodingDetector.find_declared_encoding(response.content, is_html=True)
            soup = BeautifulSoup(response.content, 'lxml', from_encoding=encoding)

            # Extract article URLs
            article_urls = {
                urljoin('https://economictimes.indiatimes.com', link.get('href'))
                for link in soup.find_all('a', href=True)
                if '/articleshow/' in link.get('href')
            }
            
            # Filter out duplicate URLs from previous iterations
            new_article_urls = list(article_urls - urls_clo)
            urls_clo.update(new_article_urls)  # Update the set of unique URLs

            # Limit the number of articles per day to avoid overwhelming
            new_article_urls = new_article_urls[:7]

            # Collect article data
            articles_data = []
            for article_url in new_article_urls:
                try:
                    title, text, source = fetch_article_content(article_url)
                    articles_data.append({
                        'title': title,
                        'text': text,
                        'source': source,
                        'url': article_url
                    })
                    print(f"Extracted: {title}")
                except Exception as e:
                    print(f"Failed to extract {article_url}: {e}")
                    continue

            # Append the data to CSV
            if articles_data:
                df = pd.DataFrame(articles_data)
                df.to_csv(csv_file, mode='a', header=not csv_exists, encoding='utf-8-sig', index=False)
                csv_exists = True  # Ensure header is not written again
                print(f"Data from {archive_url} appended to {csv_file}")
            
            # Increment the start time
            start_time_counter += 1

print("Data extraction complete. Saved to EconomicTimes_Archive.csv.")
