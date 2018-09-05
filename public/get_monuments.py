#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib
import oursql
import os
import cgi
from wmflabs import db
conn = db.connect('s53844__heritage_p')

if 'QUERY_STRING' in os.environ:
	QS = os.environ['QUERY_STRING']
	qs = cgi.parse_qs(QS)
	try:
		startswith = qs['startswith'][0]
		startswith = startswith[0].upper() + startswith[1:]
	except:
		startswith = None
	try:
		contains = qs['contains'][0]
		contains = contains[0].upper() + contains[1:]
	except:
		contains = None
else:
	startswith = None
	contains = None

print 'Content-Type: application/javascript'
print

print 'var addressPoints = ['

with conn.cursor() as cur:
	if startswith and contains:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like ? and page_title like ?', (startswith + '%', '%' + contains + '%'))
	elif startswith:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like ?', (startswith + '%', ))
	elif contains:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like ?', ('%' + contains + '%',))
	else:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null')
	data = cur.fetchall()

for row in data:
	print '\t[%s, %s, \'<img src="%s" /><br /><a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],' % (row[0], row[1], row[2], urllib.quote(row[3]), row[3])

with conn.cursor() as cur:
	if startswith and contains:
		cur.execute('select lat, lon, page_title from monuments where image is null and page_title like ? and page_title like ?', (startswith + '%', '%' + contains + '%'))
	elif startswith:
		cur.execute('select lat, lon, page_title from monuments where image is null and page_title like ?', (startswith + '%', ))
	elif contains:
		cur.execute('select lat, lon, page_title from monuments where image is null and page_title like ?', ('%' + contains + '%',))
	else:
		cur.execute('select lat, lon, page_title from monuments where image is null')
	data = cur.fetchall()

for row in data:
	print '\t[%s, %s, \'<a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],' % (row[0], row[1], urllib.quote(row[2]), row[2])
print '];'
