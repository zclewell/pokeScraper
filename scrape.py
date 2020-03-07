from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import pymongo
import  secrets

import os
import re

client_str = 'mongodb+srv://{}:{}@{}/test?retryWrites=true&w=majority'.format(secrets.get_username(), secrets.get_password(), secrets.get_server())
client = pymongo.MongoClient(client_str)
db = client.monDb
monCollection = db.monCollectionDev

def get_mons():
    os.system('mkdir data')

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
    sprite_set = set()
    orphans = []
    for filename in os.listdir('data'):
        full_name = 'data/' + filename
        with open(full_name, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            mon_name = mon_number = mon_category = mon_image = mon_sprite = None
            mon_stats = {}
            mon_types = set()
            mon_abilities = set()

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
            mon_types = [x for x in mon_types] if mon_types else None

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
                                mon_stats[key] = int(value)

            # find mon abilites
            for a in soup.find_all('a', href=True, title=True):
                if a and '(Ability)' in a.get('title'):
                    span = a.find('span')
                    if span and len(span.contents):
                        mon_abilities.add(span.contents[0])
            mon_abilities = [x for x in mon_abilities] if mon_abilities else None

            # find image
            for img in soup.find_all('img', alt=True, src=True):
                alt = img.get('alt')
                src = img.get('src')
                if mon_name == alt:
                    mon_image = src[2:] # get rid of the leading slashes
                    break
            # find sprite 
            for img in soup.find_all('img', alt=True, src=True, width=True, height=True):
                src = img.get('src')
                width = img.get('width')
                height = img.get('height')
                if width == height == '40' or width == height == '68' or width == height == '52':
                    sprite_set.add(src[2:])
            for sprite in sprite_set:
                if mon_number and (mon_number + 'MS' in sprite or mon_number + 'XYMS' in sprite):
                    mon_sprite = sprite
                    sprite_set.remove(sprite)
                    break;

            obj = {
                '_id': mon_name,
                'name': mon_name,
                'number': mon_number,
                'category': mon_category,
                'abilities': mon_abilities,
                'types': mon_types,
                'stats': mon_stats,
                'image': mon_image,
                'sprite': mon_sprite,
                'meta': sum([mon_stats[x] for x in mon_stats])
            }

            if not mon_sprite:
                orphans.append(obj)
                print('{} is an orphan! {} orphans'.format(mon_name, len(orphans)))
            else:
                pass
                print(mon_name)
                monCollection.insert_one(obj)

    for orphan in orphans:
        for sprite in sprite_set:
            number = orphan['number']
            name = orphan['name']
            if number + 'MS' in sprite or number + 'XYMS' in sprite:
                orphan['sprite'] = sprite
                sprite_set.remove(sprite)
                monCollection.insert_one(orphan)
                print('{} is no longer orphan!'.format(name))
                break
        if not orphan['sprite']:
            print('{} is uber orphan :('.format(name))
            monCollection.insert_one(orphan)
        

if __name__ == '__main__':
    get_mons()
    scan_mons()
