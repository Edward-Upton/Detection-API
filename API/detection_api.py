import flask
from numpy import random
#from flaskext.mysql import MySQL
from flask import request, make_response
import random
import string
import json
import os
from flaskext.mysql import MySQL

DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

mysql = MySQL()
APP.config['MYSQL_DATABASE_USER'] = 'pyuser'
APP.config['MYSQL_DATABASE_PASSWORD'] = 'pyuser'
APP.config['MYSQL_DATABASE_DB'] = 'charities_day'
APP.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(APP)

conn = mysql.connect()

CWD = os.path.dirname(os.path.realpath(__file__))

@APP.route('/', methods=['GET', 'POST'])
def homePage():
    return flask.render_template("home_page.html")

if __name__ == "__main__":
    try:
        APP.run(host="0.0.0.0", port=403, debug=DEBUG, ssl_context='adhoc')
    finally:
        conn.close()
