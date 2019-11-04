import cv2
import numpy as np

img = cv2.imread('images/0.jpg', 0)
edges = cv2.Canny(img, 20, 255)
im2, contours, hierarchy = cv2.findContours(
    edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

demo = cv2.drawContours(img, contours, -1, (255, 255, 0), 3)

cv2.imshow('', demo)
cv2.waitKey(0)
cv2.destroyAllWindows()
