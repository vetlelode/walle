from PIL import Image, ImageOps

for x in range(1, 9):
    im = Image.open("../sample/images/{}.jpg".format(x))
    im = ImageOps.crop(im, (0, 50, 0, 0))
    im.save('../sample/images/{}.jpg'.format(x))
