from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

import os
import re

def get_mons():
    # remove old 
    os.system('rm data/*')

    driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    base_url = 'https://bulbapedia.bulbagarden.net'
    driver.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number')

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    for a in soup.find_all('a', href=True, title=True):
        href = a.get('href')
        if 'http' not in href:
            href = base_url + href
        title = a.get('title')
        if '(Pokémon)' in title:
            with open('data/'+title, 'w') as f:
                driver.get(href)
                f.writelines(driver.page_source)

def scan_mons():
    for filename in os.listdir('data'):
        full_name = 'data/' + filename
        with open(full_name, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

            #find dex number
            for a in soup.find_all('a', href=True, title=True):
                if a.get('title') == 'List of Pokémon by National Pokédex number':
                    span = a.find('span')
                    if span:
                        match = re.search('#([0-9\?]+)',span.contents[0])
                        if match:
                            data_number = match.groups(1)[0]
                            break
            
            #find mon category
            for a in soup.find_all('a', href=True, title=True):
                if a.get('title') == 'Pokémon category':
                    span = a.find('span')
                    if span:
                        data_category = span.contents[0]
                        break
        print(data_number, data_category)

    

if __name__ == '__main__':
    # get_mons()
    scan_mons()




