#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import yaml
import pymysql
import toolforge
from urllib.parse import quote_plus
import requests
import hashlib
import time

# Load configuration
__dir__ = os.path.dirname(__file__)
config = yaml.safe_load(open(os.path.join(__dir__, '..', 'src', 'config.yaml')))

if config.get('DB_USER') and config.get('DB_PASS'):
    cache = pymysql.connect(
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        user=config['DB_USER'],
        password=config['DB_PASS'],
        charset='utf8mb4',
    )
else:
    cache = pymysql.connect(
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        read_default_file=os.path.expanduser("~/replica.my.cnf"),
        charset='utf8mb4',
    )

countries = open(os.path.join(__dir__, 'countries.txt')).read().splitlines()

with cache.cursor() as cur:
    cur.execute('TRUNCATE TABLE monuments;')

def process_url_internal(payload):
    r = requests.get('https://heritage.toolforge.org/api/api.php', params=payload)
    print(r.url)
    try:
        data = r.json()
    except:
        time.sleep(3)
        return payload
    monuments = data['monuments']
    for monument in monuments:
        if monument['monument_article'] != '' and monument['lat'] is not None and monument['lon'] is not None:
            wiki = toolforge.connect('%swiki' % monument['lang'], cluster='analytics')
            with wiki.cursor() as cur:
                monument_article = monument['monument_article'].replace(' ', '_')
                monument_article = monument_article[0].upper() + monument_article[1:]
                cur.execute('SELECT page_id FROM page WHERE page_namespace=0 AND page_title=%s', monument_article)
                if len(cur.fetchall()) == 0:
                    image = None
                    image_url = None
                    if monument['image'] != '':
                        hash = hashlib.md5(monument['image'].replace(' ', '_').encode('utf-8')).hexdigest()
                        image = monument['image']
                        image_url_name = image.replace(' ', '_')
                        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/100px-%s" % (hash[0:1], hash[0:2], image_url_name, image_url_name)
                    with cache.cursor() as cur:
                        cur.execute('INSERT INTO monuments(page_title, lat, lon, image, image_url, country, lang) VALUES (%s, %s, %s, %s, %s, %s, %s)', (
                            monument['monument_article'],
                            monument['lat'],
                            monument['lon'],
                            image,
                            image_url,
                            monument['country'],
                            monument['lang'],
                        ))
                    cache.commit()
            wiki.close()
    cache.commit()
    if data.get('continue', {}).get('srcontinue'):
        payload['srcontinue'] = data.get('continue', {}).get('srcontinue')
        return payload
    return None

def process_url(payload):
    while payload is not None:
        payload = process_url_internal(payload)


for country in countries:
    process_url({
        "action": "search",
        "srcountry": country,
        "format": "json"
    })
