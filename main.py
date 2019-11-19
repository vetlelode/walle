import picamera
import numpy as np
import easygopigo3 as easy
import atexit
import os
import glob
from PIL import Image, ImageOps
import image
import time

def cleanup():
  files = glob.glob('./images/*')
  for f in files:
    os.remove(f)


def takePhoto():
  with picamera.PiCamera() as camera:
    camera.start_preview()
    camera.resolution = (320, 240)
    output = np.empty((240, 320, 3), dtype=np.uint8)
    camera.contrast = 100
    camera.color_effects = (128, 128)
    camera.capture(output, format='rgb')
  return output

def main():
  cleanup()
  gpg = easy.EasyGoPiGo3()
  atexit.register(gpg.stop)
  atexit.register(gpg.close_eyes)

  for x in range(0, 10):
    gpg.open_eyes()
    output = takePhoto()
    im = Image.fromarray(output)
    im.save('images/{}.jpg'.format(x))
    gpg.close_eyes()
    ang, shift = image.process("images/{}.jpg".format(x), False)
    if (ang >= 85 and ang <= 95):
        gpg.forward()
        time.sleep(0.5)
        gpg.stop() 


if __name__ == "__main__":
  main()
