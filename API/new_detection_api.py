import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
import cv2
from io import StringIO, BytesIO
import numpy as np
import base64
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

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

    return Image.fromarray(cv_image)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        img_io = BytesIO()
        image_PIL.save(img_io, 'JPEG')
        img_io.seek(0)
        img_base64 = str(base64.b64encode(img_io.getvalue()))
        img_str = img_base64[2:len(img_base64)-1]
        print(img_str)
        imageBase64_str = "data:image/jpeg;base64,{}".format(img_str)
        return render_template('uploaded_image.html', imageBase64=imageBase64_str)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)