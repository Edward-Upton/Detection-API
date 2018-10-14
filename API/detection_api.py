import flask
import re
import numpy as np 
#from flaskext.mysql import MySQL
from flask import request, make_response
import string
import json
import os
#import object_detection_runner
from PIL import Image
import cv2
import codecs
from datauri import DataURI
from io import BytesIO, StringIO
import base64
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

@APP.route('/detect', methods=['GET', 'POST'])
def detect():

    image_b64 = request.values['imageBase64']
    image_data = re.sub('^data:image/.+;base64,', '', image_b64).decode('base64')
    image_PIL = Image.open(StringIO(image_b64))
    image_np = np.array(image_PIL)

    image_PIL.show()

    #open_cv_image = np.array(image.convert('RGB'))

    #pil_img = Image.fromarray(open_cv_image) 

    #parts_dict = object_detection_runner.detect_objects(image_PIL)


    #return str(parts_dict)
    
if __name__ == "__main__":
    try:
        APP.run(host="0.0.0.0", port=80, debug=DEBUG, ssl_context='adhoc')
    finally:
        conn.close()
