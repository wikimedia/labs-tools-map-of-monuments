#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import yaml
import pymysql
import toolforge
from urllib.parse import quote_plus
import hashlib

# Load configuration
config = yaml.safe_load(open('config.yaml'))

# Get database connections
cswiki = toolforge.connect('cswiki')
cache = pymysql.connect(
	database=config['DB_NAME'],
	host='tools.db.svc.eqiad.wmflabs',
	read_default_file=os.path.expanduser("~/replica.my.cnf"),
	charset='utf8mb4',
)

with cswiki.cursor() as cur:
	sql = 'select replace(pl_title, "_", " ") from pagelinks join page on pl_from=page_id where page_title like "Seznam_kulturních_památek%" and pl_namespace=0 and pl_title not in (select page_title from page where page_namespace=0);'
	cur.execute(sql)
	data = cur.fetchall()

with cache.cursor() as cur:
	cur.execute('delete from monuments_cache;')
for row in data:
	with cache.cursor() as cur:
		cur.execute('insert into monuments_cache(page_title) values(%s)', row[0])
cache.commit()


with cache.cursor() as cur:
	cur.execute('delete from monuments;')
with cache.cursor() as cur:
	cur.execute('insert into monuments (page_title, lat, lon, image, country) select monument_article, lat, lon, image, "cs" from monuments_cache join s51138__heritage_p.`monuments_cz_(cs)` on monument_article=page_title where image!="" and lat is not null and lon is not null')
with cache.cursor() as cur:
	cur.execute('insert into monuments (page_title, lat, lon, image, country) select monument_article, lat, lon, NULL, "cs" from monuments_cache join s51138__heritage_p.`monuments_cz_(cs)` on monument_article=page_title where image="" and lat is not null and lon is not null')
with cache.cursor() as cur:
	cur.execute('delete from monuments_cache;')
cache.commit()

with cache.cursor() as cur:
	cur.execute('select id, image from monuments where image is not null')
	data = cur.fetchall()
	for row in data:
		with cache.cursor() as cur2:
			cur2.execute('update monuments set image_url=%s where id=%s', ("https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/100px-%s" % (hashlib.md5(row[1].replace(' ', '_').encode('utf-8')).hexdigest()[0:1], hashlib.md5(row[1].replace(' ', '_').encode('utf-8')).hexdigest()[0:2], row[1].replace(' ', '_'), row[1].replace(' ', '_')), row[0]))
	cache.commit()
