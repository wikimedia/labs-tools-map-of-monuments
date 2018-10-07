#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import yaml
import pymysql
import toolforge
from urllib.parse import quote_plus
import requests
import hashlib

# Load configuration
config = yaml.safe_load(open('../src/config.yaml'))

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

countries = open('countries.txt').read().splitlines()

with cache.cursor() as cur:
    cur.execute('TRUNCATE TABLE monuments;')

def process_url(payload):
    r = requests.get('https://tools.wmflabs.org/heritage/api/api.php', params=payload)
    print(r.url)
    data = r.json()
    monuments = data['monuments']
    for monument in monuments:
        if monument['monument_article'] != '' and monument['lat'] is not None and monument['lon'] is not None:
            wiki = toolforge.connect('%swiki' % monument['lang'])
            with wiki.cursor() as cur:
                cur.execute('SELECT page_id FROM page WHERE page_namespace=0 AND page_title=%s', monument['monument_article'].replace(' ', '_'))
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
            wiki.close()
    cache.commit()
    if data.get('continue', {}).get('srcontinue'):
        payload['srcontinue'] = data.get('continue', {}).get('srcontinue')
        process_url(payload)


for country in countries:
    process_url({
        "action": "search",
        "srcountry": country,
        "format": "json"
    })
