import requests
import datetime
import pandas as pd
import re
from urllib.parse import urljoin
from goose3 import Goose
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

# Get the Current Year
now = datetime.date.today()
year  = [  "2022" , "2023" ]


# Get the Current Month
month = ["1","2","3","4","5","6","7","8","9","10","11","12"]


# Enter the URL to check for news
url = 'https://www.opindia.com/'
# Append this url for all the articles
url1 = 'https://www.opindia.com/'
# Match the pattern in all the url's
pattern = 'https://www.opindia.com/' 
ran = ["1"]
csv_file = 'OPTimes_DataSet.csv'
for i in year:
    
    for j in month:
        final_urls = []
        for k in ran:
          response = requests.get('https://www.opindia.com/'+i+ '/' +j+ '/page/'+k)
          http_encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
          html_encoding = EncodingDetector.find_declared_encoding(response.content, is_html=True)
          encoding = html_encoding or http_encoding

# Specify the parser explicitly
          soup = BeautifulSoup(response.content, features="lxml")

          
# Get the list of hyperlinks on the page
          for link in soup.find_all('a'):
            href = link.attrs.get("href")
            href = urljoin(url1, href)
            if pattern in href:
              final_urls.append(href)
        print(len(final_urls))
        unique_urls_list = list(final_urls)  
        final_title_list = []
        final_text_list = []
        final_source_list = []
        final_image_list = []

        for data in unique_urls_list:
            g = Goose()
            article = g.extract(url=data)
            title = article.title
            text = article.cleaned_text
            domain = article.domain
            image = article.infos  # Assuming this is correct; adjust as necessary
    
            source = re.findall(r'(?<=\.)([^.]+)(?:\.(?:co\.uk|ac\.us|[^.]+(?:$|\n)))', domain)
    
            final_title_list.append(title)
            final_text_list.append(text)
            final_source_list.extend(source)
           
# Create a DataFrame
        dict_1 = {'title': final_title_list, 'text': final_text_list, 'author': final_source_list}
        df = pd.DataFrame({key: pd.Series(value) for key, value in dict_1.items()})
        file_exists = True
# Save to CSV with utf-8-sig encoding
        df.to_csv('OPTimes_DataSet.csv',mode='a', header=not file_exists, encoding='utf-8-sig', index=False)
        print("appended")    
# Remove duplicate URLs        
print("Data extraction complete. Saved to OPTimes_DataSet.csv.")