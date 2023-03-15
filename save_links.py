# https://ruxpert.ru/Список_государственных_сайтов_России
# https://www.garant.ru/doc/busref/spr_gos_site/

import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Get the URL from the command-line argument
if len(sys.argv) < 2:
    print("Usage: python script.py url")
    sys.exit(1)

url = sys.argv[1]

# Make a request to the webpage
response = requests.get(url)

# Parse the HTML content of the webpage using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the links on the webpage
links = soup.find_all('a')

# Save the href attribute of each link to a text file
with open('links.txt', 'w') as file:
    for link in links:
        href = link.get('href')
        if href is not None:
            if not href.startswith('/'):
                parsed_href = urlparse(href)
            # If the netloc is not empty and ends with .ru, keep only the netloc
            if parsed_href.netloc and parsed_href.netloc.endswith('.ru'):
                file.write(parsed_href.netloc + '\n')
