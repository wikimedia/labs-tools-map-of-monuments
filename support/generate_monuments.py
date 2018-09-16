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

cache = pymysql.connect(
	database=config['DB_NAME'],
	host='tools.db.svc.eqiad.wmflabs',
	read_default_file=os.path.expanduser("~/replica.my.cnf"),
	charset='utf8mb4',
)

countries = ['cz']

with cache.cursor() as cur:
	cur.execute('TRUNCATE TABLE monuments;')

def process_url(url):
	r = requests.get(url)
	data = r.json()
	monuments = data['monuments']
	for monument in monuments:
		if monument['monument_article'] != '':
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
						cur.execute('INSERT INTO monuments(page_title, lat, lon, image, image_url, country) VALUES (%s, %s, %s, %s, %s, %s)', (
							monument['monument_article'],
							monument['lat'],
							monument['lon'],
							image,
							image_url,
							monument['country']
						))
	if data.get('continue', {}).get('srcontinue'):
		process_url(url + '&srcontinue=%s' % data.get('continue', {}).get('srcontinue'))


for country in countries:
	process_url('https://tools.wmflabs.org/heritage/api/api.php?action=search&srcountry=%s&format=json' % country)
	cache.commit()
