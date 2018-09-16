# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import flask
from flask import redirect, request, jsonify, make_response, render_template, Response
import os
import yaml
import pymysql
import urllib

app = flask.Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

def connect():
    return pymysql.connect(
        database=app.config['DB_NAME'],
        host=app.config['DB_HOST'],
        read_default_file=os.path.expanduser("~/replica.my.cnf"),
        charset='utf8mb4'
    )

@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(
            'https://' + request.headers['Host'] + request.headers['X-Original-URI'],
            code=301
        )

@app.route('/')
def index():
    return render_template('index.html', startswith=request.args.get('startswith', ''), contains=request.args.get('contains', ''))

@app.route('/get_monuments')
def get_monuments():
    conn = connect()
    startswith = request.args.get('startswith', None)
    contains = request.args.get('contains', None)
    javascript = "var addressPoints = [\n"
    with conn.cursor() as cur:
        if startswith and contains:
            cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like %s and page_title like %s', (startswith + '%', '%' + contains + '%'))
        elif startswith:
            cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like %s', (startswith + '%', ))
        elif contains:
            cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null and page_title like %s', ('%' + contains + '%',))
        else:
            cur.execute('select lat, lon, replace(image_url, "\'", "\\\\\'"), page_title from monuments where image is not null')
        data = cur.fetchall()
    for row in data:
        javascript += '\t[%s, %s, \'<img src="%s" /><br /><a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],\n' % (row[0], row[1], row[2], urllib.parse.quote(row[3]), row[3])

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
        javascript += '\t[%s, %s, \'<a target="_blank" href="https://cs.wikipedia.org/wiki/%s?veaction=edit">%s</a>\'],\n' % (row[0], row[1], urllib.parse.quote(row[2]), row[2])

    javascript += '];'
    return Response(javascript, mimetype="text/javascript")


if __name__ == "__main__":
        app.run(debug=True, threaded=True)
