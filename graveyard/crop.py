from PIL import Image, ImageOps

im = Image.open("../sample/straightLine/0.jpg")
im = ImageOps.crop(im, (0, 50, 0, 0))
im.save('../sample/0.jpg')
