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

for country in countries:
	r = requests.get('https://tools.wmflabs.org/heritage/api/api.php?action=search&srcountry=%s&format=json' % country)
	monuments = r.json()['monuments']
	for monument in monuments:
		if monument['monument_article'] != '':
			wiki = toolforge.connect('%swiki' % monument['lang'])
			with wiki.cursor() as cur:
				cur.execute('SELECT page_id FROM page WHERE page_namespace=0 AND page_title=%s', monument['monument_article'])
				if len(cur.fetchall()) == 0:
					image_url = None
					if monument['image'] != '':
						hash = hashlib.md5(monument['image'].replace(' ', '_')).hexdigest()
						image_url_name = urllib.parse.quote(monument['image'].replace(' ', '_'))
						image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/100px-%s" % (hash[0:1], hash[0:2], image_url_name, image_url_name)