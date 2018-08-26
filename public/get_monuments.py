#!/usr/bin/env python
#-*- coding: utf-8 -*-

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
	except:
		startswith = None

print 'Content-Type: application/javascript'
print

print 'var addressPoints = ['

with conn.cursor() as cur:
	if startswith:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where page_title like ?', (startswith + '%', ))
	else:
		cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments')
	data = cur.fetchall()

for row in data:
	print '\t[%s, %s, \'<img src="%s" /><br /><a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],' % (row[0], row[1], row[2], "a", row[3])
print '];'
