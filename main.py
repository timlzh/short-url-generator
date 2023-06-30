from flask import *
from urlShortener import *
import os
from configparser import ConfigParser

config = ConfigParser()

config.read('config.ini')

port = config['server']['port']
base_url = config['server']['base_url']

if base_url[-1] != '/':
    base_url += '/'

db_host = config['database']['host']
db_port = config['database']['port']
db_db = config['database']['db']
db_collection = config['database']['collection']

db_login = bool(int(config['database']['login']))
db_user = config['database']['user'] if db_login else None
db_password = config['database']['password'] if db_login else None

urlShortener = UrlShortener(db_host, int(db_port), db_db, db_collection, db_login, db_user, db_password)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

def alert(msg, redirect):
    return "<script>alert('{}');window.location.href='{}';</script>".format(msg, redirect)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gen', methods=['POST'])
def gen():
    url=request.form['url']
    try:
        short_url = urlShortener.shorten_url(url)
        return render_template('gen.html', url=base_url + short_url)
    except InvalidUrlError:
        return alert('Invalid URL', '/')

@app.route('/<short_url>', methods=['GET'])
def redirect_short_url(short_url):
    url = urlShortener.get_url(short_url)
    if url is None:
        return abort(404)
    else:
        return redirect(url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))