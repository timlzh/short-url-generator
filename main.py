"""
@Author: Timlzh <2921349622@qq.com>
"""
import os
from configparser import ConfigParser

from flask import Flask, render_template, request, redirect, abort

from url_shortener import UrlShortener, InvalidUrlError

config = ConfigParser()

config.read('config.ini')

port = config['server']['port']
base_url = config['server']['base_url']

if base_url[-1] != '/':
    base_url += '/'

db_host = config['database']['host']
db_port = config['database']['port']

db_login = bool(int(config['database']['login']))
db_user = config['database']['user'] if db_login else None
db_password = config['database']['password'] if db_login else None

urlShortener = UrlShortener((db_host, int(db_port)),
                            db_login, db_user, db_password)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def alert(msg: str, redirect_url: str) -> str:
    """alert

    Args:
        msg (str): Message to alert
        redirect_url (str): Redirect url after alert

    Returns:
        str: alert script
    """
    return f"<script>alert('{msg}');window.location.href='{redirect_url}';</script>"


@app.errorhandler(404)
def page_not_found(_) -> tuple:
    """
        404 Error Handler
    """
    return render_template('404.html'), 404


@app.route('/')
def index() -> str:
    """index_page

    Returns:
        str: index page
    """
    return render_template('index.html')


@app.route('/gen', methods=['POST'])
def gen() -> str:
    """gen_short_url_page

    Returns:
        str: short url page
    """
    url = request.form['url']
    try:
        short_url = urlShortener.shorten_url(url)
        return render_template('gen.html', url=base_url + short_url)
    except InvalidUrlError:
        return alert('Invalid URL', '/')


@app.route('/<short_url>', methods=['GET'])
def redirect_short_url(short_url):
    """redirect_short_url_page

    Args:
        short_url (str): short url

    Returns:
        str: redirect page
    """
    url = urlShortener.get_url(short_url)
    return abort(404) if url is None else redirect(url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port))
