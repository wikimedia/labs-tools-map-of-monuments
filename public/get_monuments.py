#!/usr/bin/env python
#-*- coding: utf-8 -*-

from wmflabs import db
conn = db.connect('s53844__heritage_p')

print 'Content-Type: application/javascript'
print

print 'var addressPoints = ['

with conn.cursor() as cur:
	cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments')
	data = cur.fetchall()

for row in data:
	print '\t[%s, %s, \'<img src="%s" /><br /><a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],' % (row[0], row[1], row[2], "a", row[3])
print '];'
