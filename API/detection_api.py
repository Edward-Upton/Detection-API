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
from io import BytesIO, StringIO
import base64
from flaskext.mysql import MySQL
from binascii import a2b_base64

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
    requestData = request.json
    image_data = requestData["imageBase64"]
    content = image_data.split(';')[1]
    image_encoded = content.split(',')[1]
    body = base64.decodebytes(image_encoded.encode('utf-8'))
    image_PIL = Image.open(BytesIO(body))
    with open("image.png", "wb") as fp:
        fp.write(body)
    image_np = np.array(image_PIL.convert('RGB'))

    open_cv_image = np.array(image_np)
    # cv2.imshow('image',cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    image_PIL = Image.fromarray(open_cv_image)

    (im_width, im_height) = image_PIL.size
    print(np.array(image_PIL.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8))

    #parts_dict = object_detection_runner.detect_objects(image_PIL)

    return "Success"


if __name__ == "__main__":
    try:
        APP.run(host="0.0.0.0", port=80, debug=DEBUG, ssl_context='adhoc')
    finally:
        conn.close()
