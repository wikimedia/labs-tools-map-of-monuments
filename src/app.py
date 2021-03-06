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
from flask_jsonlocale import Locales

app = flask.Flask(__name__, static_folder='../static')
locales = Locales(app)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

def connect():
    if app.config.get('DB_USER') and app.config.get('DB_PASS'):
        return pymysql.connect(
            database=app.config['DB_NAME'],
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASS'],
            charset='utf8mb4'
        )
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

@app.before_request
def check_maintenance():
    if app.config.get('MAINTENANCE', False):
        return render_template('maintenance.html')

@app.before_request
def urlencode_into_template():
    app.jinja_env.globals.update(quote=urllib.parse.quote)

@app.context_processor
def add_campaign():
    return {
        "campaign": request.args.get('campaign')
    }

@app.route('/')
def index():
    return render_template('index.html', startswith=request.args.get('startswith', ''), contains=request.args.get('contains', ''), images=request.args.get('images'), countries=request.args.get('countries', ''))

@app.route('/get_monuments')
def get_monuments():
    conn = connect()
    startswith = request.args.get('startswith', '')
    contains = request.args.get('contains', '')
    images = request.args.get('images', None)
    countries = request.args.get('countries')
    if countries:
        countries = countries.split('|')
    else:
        countries = []
    if images == "True":
        images = True
    elif images == "False":
        images = False
    else:
        images = None
    points = []

    with conn.cursor() as cur:
        if len(countries) > 0:
            countries_sql = ' and country in (%s)' % (', '.join(['%s'] * len(countries)))   # HACK: There's gotta be a more nice way
        else:
            countries_sql = ''
        cur.execute('select lat, lon, image_url, page_title, lang from monuments where page_title like %s and page_title like %s' + countries_sql, (startswith + '%', '%' + contains + '%') + tuple(countries))
        data = cur.fetchall()

    for row in data:
        if row[2] is not None and images is False:
            continue
        if row[2] is None and images is True:
            continue

        if row[2]:
            image = '<img src="%s" /><br />' % row[2]
        else:
            image = ''
        html = image + '<a class="redlink" target="_blank" href="https://%s.wikipedia.org/wiki/%s?veaction=edit">%s</a>' % (row[4], urllib.parse.quote(row[3]), row[3])
        points.append([row[0], row[1], html, row[3]])

    return jsonify(points)

@app.route('/list-of-monuments')
def list_of_monuments():
    conn = connect()
    with conn.cursor() as cur:
        cur.execute('select distinct lang from monuments')
        langs = cur.fetchall()
    return render_template('langs.html', langs=langs)

@app.route('/list-of-monuments/<lang>')
def list_of_monuments_lang(lang):
    conn = connect()
    startswith = request.args.get('startswith', '')
    contains = request.args.get('contains', '')

    with conn.cursor() as cur:
        cur.execute('select page_title, lang from monuments where page_title like %s and page_title like %s and lang=%s', (startswith + '%', '%' + contains + '%', lang))
        data = cur.fetchall()
    monuments = []
    for row in data:
        monuments.append({
            'lang': row[1],
            'url_encoded_title': urllib.parse.quote(row[0]),
            'title': row[0]
        })
    return render_template('monuments.html', monuments=monuments)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
