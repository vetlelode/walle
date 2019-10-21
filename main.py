import picamera
import numpy as np
import easygopigo3 as easy
import atexit
import os
import glob

def cleanup():
  files = glob.glob('./images/*')
  for f in files:
    os.remove(f)


def takePhoto():
  with picamera.PiCamera() as camera:
    camera.start_preview()
    camera.resolution = (640, 480)
    output = np.empty((480, 640, 3), dtype=np.uint8)
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
    print(output.shape)
    #name = 'images/{}.jpg'.format(x)
    #img.save(name)


if __name__ == "__main__":
  main()
