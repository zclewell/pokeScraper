from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

import os
import re

def get_mons():
    # remove old 
    os.system('mkdir data')
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
            mon_name = mon_number = mon_category = None
            mon_stats = {}
            mon_types = set()
            mon_abilties = set()

            # find name
            for big in soup.find_all('big'):
                big_big = big.find('big')
                if big_big:
                    big_big_b = big_big.find('b')
                    if big_big_b:
                        mon_name = big_big_b.contents[0]
                        break

            # find dex number
            for a in soup.find_all('a', href=True, title=True):
                if a.get('title') == 'List of Pokémon by National Pokédex number':
                    span = a.find('span')
                    if span:
                        match = re.search('#([0-9\?]+)',span.contents[0])
                        if match:
                            mon_number = match.groups(1)[0]
                            break

            # find mon types
            # TODO handle multiform mons
            for table in soup.find_all('table', style=True):
                if 'margin:auto; background:none;' != table.get('style'):
                    continue
                for tbody in table.find_all('tbody'):
                    for tr in tbody.find_all('tr'):
                        for td in tr.find_all('td'):
                            for a in td.find_all('a', href=True, title=True):
                                title = a.get('title')
                                if title and '(type)' in title:
                                    span = a.find('span')
                                    if span:
                                        b = span.find('b')
                                        if b:
                                            content = b.contents[0]
                                            if not content == 'Unknown':
                                                mon_types.add(b.contents[0])
            mon_types = [x for x in mon_types]

            # find mon category
            for a in soup.find_all('a', href=True, title=True):
                if a.get('title') == 'Pokémon category':
                    span = a.find('span')
                    if span:
                        explain = span.find('span')
                        if explain:
                            mon_category = explain.contents[0]
                        else:
                            mon_category = span.contents[0]
                        break
            
            # find mon stats
            for th in soup.find_all('th', style=True):
                if th and th.get('style') == 'width:85px; padding-left:0.5em; padding-right:0.5em':
                    a = th.find('a', href=True, title=True)
                    if a and a.get('title') == 'Statistic':
                        key = a.find('span').contents[0].replace('.','')
                        for div in th.find_all('div', style=True):
                            if div and div.get('style') == 'float:right':
                                value = div.contents[0]
                                mon_stats[key] = value

            # find mon abilites
            for a in soup.find_all('a', href=True, title=True):
                if a and '(Ability)' in a.get('title'):
                    span = a.find('span')
                    if span:
                        mon_abilties.add(span.contents[0])
            mon_abilties = [x for x in mon_abilties]




if __name__ == '__main__':
    get_mons()
    scan_mons()
