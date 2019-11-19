import cv2
import numpy as np
import geo as geom


def process(im, demo=True):
    img = cv2.imread(im, 0)
    h, w = img.shape
    edges = cv2.Canny(img, 20, 255, apertureSize=3)
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    C = None
    if contours is not None and len(contours) > 0:
        C = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(C)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        box = geom.order_box(box)
        print(box)
        p1, p2 = geom.calc_box_vector(box)
        angle = geom.get_vert_angle(p1, p2, w, h)
        shift = geom.get_horz_shift(p1[0], w)
        print("Angle: {0}\nShift: {1}\nBox: {2}{3}".format(
            angle, shift, p1, p2))

        if demo:
            # Render an illustration of the contour detection
            cv2.drawContours(img, [box], 0, (100, 100, 100), 10)
            cv2.drawContours(img, [box], 0, (255, 0, 0), 2)
            cv2.line(img, (int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])), (0, 255, 0), 10)
            msg_a = "Angle {0}".format(int(angle))
            msg_s = "Shift {0}".format(int(shift))
            cv2.putText(img, msg_a, (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)
            cv2.putText(img, msg_s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 1)
            cv2.imshow('', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


def process_pic(image):
    global Roi
    global T
    height, width = image.shape[:2]

    gray = cv.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (9, 9), 0)

    if Roi.get_area() == 0:
        Roi.init_roi(width, height)

    return balance_pic(blurred), width, height


def balance_pic(image):
    global T
    ret = None
    direction = 0
    for i in range(0, 5):

        rc, gray = cv2.threshold(image, T, 255, 0)
        crop = Roi.crop_roi(gray)

        nwh = cv2.countNonZero(crop)
        perc = int(100 * nwh / Roi.get_area())
        if perc > tconf.white_max:
            if T > tconf.threshold_max:
                break
            if direction == -1:
                ret = crop
                break
            T += 10
            direction = 1
        elif perc < tconf.white_min:
            if T < tconf.threshold_min:
                break
            if direction == 1:
                ret = crop
                break

            T -= 10
            direction = -1
        else:
            ret = crop
            break
    return ret


process("sample/straightLine/0.jpg")
process("sample/mordi.jpg")
process("sample/test.jpg")
