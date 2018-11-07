
import flask
import re
import numpy as np
from flask import request, make_response
import string
import json
import os
import object_detection_runner
from PIL import Image
import cv2
import codecs
from io import BytesIO, StringIO
import base64
from flaskext.mysql import MySQL
from binascii import a2b_base64

DEBUG = False
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

# mysql = MySQL()
# APP.config['MYSQL_DATABASE_USER'] = 'pyuser'
# APP.config['MYSQL_DATABASE_PASSWORD'] = 'pyuser'
# APP.config['MYSQL_DATABASE_DB'] = 'charities_day'
# APP.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(APP)

# conn = mysql.connect()

CWD = os.path.dirname(os.path.realpath(__file__))

IMAGE_RESOLUTION = [300,300]


@APP.route('/', methods=['GET', 'POST'])
def homePage():
    return flask.render_template("home_page.html")


@APP.route('/detect', methods=['GET', 'POST'])
def detect(): 
    image_data = request.form.get("imageBase64")
    content = image_data.split(';')[1]
    image_encoded = content.split(',')[1]
    body = base64.decodebytes(image_encoded.encode('utf-8'))
    image_PIL = Image.open(BytesIO(body))
    image_np = np.array(image_PIL.convert('RGB'))

    cv_image = np.array(image_np)
    height_diff = abs(cv_image.shape[0]-IMAGE_RESOLUTION[0])
    width_diff = abs(cv_image.shape[1]-IMAGE_RESOLUTION[1])

    if width_diff <= height_diff:
        #Landscape
        scale_image = IMAGE_RESOLUTION[1] / cv_image.shape[1]
        new_width = int(scale_image*cv_image.shape[1])
        new_height = int(scale_image*cv_image.shape[0])
        cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        ycrop_min = int(abs(IMAGE_RESOLUTION[0] - cv_image.shape[0]) / 2)
        ycrop_max = int(cv_image.shape[0] - (abs(IMAGE_RESOLUTION[0] - cv_image.shape[0]) / 2))

        print("Y", ycrop_min, ycrop_max)

        cv_image = cv_image[ycrop_min:ycrop_max, : , :]

    elif width_diff > height_diff:
        #Portrait
        scale_image = IMAGE_RESOLUTION[0] / cv_image.shape[0]
        new_width = int(scale_image*cv_image.shape[1])
        new_height = int(scale_image*cv_image.shape[0])
        cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        xcrop_min = int(abs(IMAGE_RESOLUTION[1] - cv_image.shape[1]) / 2)
        xcrop_max = int(cv_image.shape[1] - (abs(IMAGE_RESOLUTION[1] - cv_image.shape[1]) / 2))

        print("X", xcrop_min, xcrop_max)

        cv_image = cv_image[ : , xcrop_min:xcrop_max, :]
        
    cv2.imwrite('resizing_test_cv2.png', cv_image)

    

    # cv2.imshow('image',cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2RGB))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    image_PIL = Image.fromarray(cv_image)
    image_PIL.show()

    detectedParts = object_detection_runner.detect_objects(image_PIL)
    print(str(detectedParts))
    if len(detectedParts) == 0:
        return "No Bricks Were Detected"
    else:
        return flask.render_template("detection.html", detectedParts = detectedParts)
if __name__ == "__main__":
    try:
        APP.run(host="0.0.0.0", port=80, debug=DEBUG)
    finally:
        #conn.close()
        print("Done")