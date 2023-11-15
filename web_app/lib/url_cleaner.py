import csv
from urllib.parse import urlparse
import re

toponemillion = set()
csv_file = "lib/top-1m.csv"
with open(csv_file, mode='r', newline='') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        if len(row) >= 2:
            toponemillion.add(row[1])

urls_on_popular_domains, urls_on_un_popular_domains = [], []

class url_cleaner:
    def __init__(self):
        pass

    # Remove protocal and any www
    def clean_urls(self, urls):
        results = []
        for url in urls:
            cleaned_url = re.sub(r'https?://', '', url['url'])  # Removes http:// or https://
            cleaned_url = re.sub(r'www\.', '', cleaned_url)  # Removes www.
            cleaned_url = re.sub(r':\d+$', '', cleaned_url)  # Removes :portnumbers.
            cleaned_url = cleaned_url.lower()  # Converts to lowercase
            url['url'] = cleaned_url
            results.append(url)
        return results
    
    def separate_redirections(self, urls):
        results = []
        for url in urls:
            if 'http=' in url:    
                results.append(url)
        return results

    def remove_popular_domains(self, urls):
        results = []
        for url in set(urls):
            url = url.strip()
            if "http" not in url:
                protocoled_url = "http://" + url # have to add potocol to be parsed correctly
            else:
                protocoled_url = url
            domain = urlparse(protocoled_url).netloc 
            domain = re.sub(r':\d+$', '', domain) # have to clean the URL here for some reason, but also left it in clean_urls.
            if domain in toponemillion:
                popularity = {'domain': domain, 'result': 'popular', 'url': url}
                results.append(popularity)
            else:
                popularity = {'domain': domain, 'result': 'unpopular', 'url': url}
                results.append(popularity)
        return(results)