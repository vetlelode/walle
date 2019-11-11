import cv2
import numpy as np
import geo as geom

img = cv2.imread('images/0.jpg', 0)
edges = cv2.Canny(img, 20, 255, apertureSize=3)
im2, contours, hierarchy = cv2.findContours(
    edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#demo = cv2.drawContours(edges, contours, -1, (255, 255, 0), 3)
C = None
if contours is not None and len(contours) > 0:
    C = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(C)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    box = geom.order_box(box)
    p1, p2 = geom.calc_box_vector(box)
    angle = geom.get_vert_angle(p1, p2, 320, 240)
    shift = geom.get_horz_shift(p1[0], 320)
    print("Angle: {0}\nShift: {1}\nBox: {2}{3}".format(angle,shift,p1,p2))

    demo = cv2.drawContours(img,[box],0,(255,0,0),2)
    cv2.line(img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 255, 0), 3)
    msg_a = "Angle {0}".format(int(angle))
    msg_s = "Shift {0}".format(int(shift))
    cv2.putText(img, msg_a, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    cv2.putText(img, msg_s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)


cv2.imshow('', demo)
cv2.waitKey(0)
cv2.destroyAllWindows()
