import base64

with open("imageBS64.txt") as fp:
    base64img = fp.read

with open("imageToSave.png", "wb") as fh:
    fh.write(base64.decodestring(base64img))