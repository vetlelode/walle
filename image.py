import cv2
import numpy as np
import geo as geom

def process(im, demo=True):
    img = cv2.imread(im)
    h, w, chn = img.shape
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    cv2.drawContours(img, contours, 0, (0, 0, 255), 1)
    cv2.imshow('', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
     
