import os
from flask import Flask, flash, request, redirect, url_for, render_template
import requests
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags, ImageDraw
import cv2
from io import StringIO, BytesIO
import numpy as np
import base64
import object_detection_runner
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

DEBUG = False
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

IMAGE_RESOLUTION = [300,300]

def processImage(imagePIL):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(imagePIL._getexif().items())

        if exif[orientation] == 3:
            imagePIL=imagePIL.rotate(180, expand=True)
        elif exif[orientation] == 6:
            imagePIL=imagePIL.rotate(270, expand=True)
        elif exif[orientation] == 8:
            imagePIL=imagePIL.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    image_np = np.array(imagePIL.convert('RGB'))

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

        cv_image = cv_image[ycrop_min:ycrop_max, : , :]

    elif width_diff > height_diff:
        #Portrait
        scale_image = IMAGE_RESOLUTION[0] / cv_image.shape[0]
        new_width = int(scale_image*cv_image.shape[1])
        new_height = int(scale_image*cv_image.shape[0])
        cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        xcrop_min = int(abs(IMAGE_RESOLUTION[1] - cv_image.shape[1]) / 2)
        xcrop_max = int(cv_image.shape[1] - (abs(IMAGE_RESOLUTION[1] - cv_image.shape[1]) / 2))

        cv_image = cv_image[ : , xcrop_min:xcrop_max, :]

    return Image.fromarray(cv_image)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/info', methods=['GET'])
def info():
    return render_template("info.html")

@app.route('/image_upload', methods=['GET', 'POST'])
def image_upload():
    return render_template("image_upload.html")

@app.route('/uploaded_image', methods=['GET', 'POST'])
def uploaded_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect("/image_upload")
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect("/image_upload")
    if file and allowed_file(file.filename):
        image_PIL = Image.open(file.stream)
        image_PIL = processImage(image_PIL)
        detectedParts = object_detection_runner.detect_objects(image_PIL)
        # image_draw = ImageDraw.Draw(image_PIL)
        # for brick in detectedParts:
        #     coordinates = brick["coordinates"]
        #     rel_coordinates = [i * 300 for i in coordinates]
        #     rounded_rel_coordinates = [round(x) for x in rel_coordinates]
        #     image_draw.rectangle(rounded_rel_coordinates, outline="white")
        detectedPartsData = []
        img_io = BytesIO()
        image_PIL.save(img_io, 'JPEG')
        img_io.seek(0)
        img_base64 = str(base64.b64encode(img_io.getvalue()))
        img_str = img_base64[2:len(img_base64)-1]
        imageBase64_str = "data:image/jpeg;base64,{}".format(img_str)

        for brick in detectedParts:
            headers = {"key":"8ee516adb0c216f432ae6d9d0f0101b8"}
            brickData = requests.get("https://rebrickable.com/api/v3/lego/parts/%s/" % str(brick["partID"]), params=headers)
            brickData = brickData.json()
            brickDataDict = dict()
            brickDataDict["name"] = brickData["name"]
            brickDataDict["partID"] = brickData["part_num"]
            brickDataDict["confidence"] = brick["confidence"]
            brickDataDict["url"] = brickData["part_url"]
            brickDataDict["img"] = brickData["part_img_url"]
            brickDataDict["uniqueID"] = brick["uniqueID"]
            detectedPartsData.append(brickDataDict)

        return render_template("detection.html", uploadedImgStrBase64=imageBase64_str, detectedPartsData = detectedPartsData)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=DEBUG)