from PIL import Image, ImageDraw

imagePIL = Image.open("API/Brick2x4Normal.jpg")
image_draw = ImageDraw.Draw(imagePIL)
image_draw.rectangle([45,150,70,200], outline="white")
imagePIL.show()