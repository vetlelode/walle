#!/usr/bin/python
import io
import picamera
import cv2
import numpy as np
import sys
import math
import serial
import move
from simple_pid import PID


# The grey image is used for most of the calculations and isn't displayed
WINDOW_GRAY_IMAGE = 'gray image'
# This is displayed on screen with overlays showing the line tracking
WINDOW_DISPLAY_IMAGE = 'display image'
RESOLUTION_X = 320
RESOLUTION_Y = 240

DEMO = True
MOVE = True
# This is half the width of the line at the bottom of the screen that we start looking for
# the line we want to follow.
SCAN_RADIUS = RESOLUTION_X / 2
# Start the scan height 10 pixels from the bottom.
SCAN_HEIGHT = RESOLUTION_Y - 5
# This is our centre. We assume that we want to try and track the line in relation to this point
SCAN_POS_X = RESOLUTION_X / 2
# This is the radius that we scan from the last known point for each of the circles
SCAN_RADIUS_REG = 85
# The number of itterations we scan to allow us to look ahead and give us more time
# to make better choices
NUMBER_OF_CIRCLES = 1
pid = PID(1, 0.1, 0.05, setpoint=0)


def scanLine(image, display_image, point, radius):
    x = point[0]
    y = point[1]

    scan_start = x - radius
    scan_end = x + radius
    row = image[y]
    data = np.empty(radius*2)
    data[:] = row[scan_start:scan_end]

    # Draw a line where we are reading the data
    cv2.line(display_image, (scan_start, y), (scan_end, y), (255, 0, 0), 2)
    cv2.circle(display_image, (scan_start, y), 5, (255, 0, 0), -1, 8, 0)
    cv2.circle(display_image, (scan_end, y), 5, (255, 0, 0), -1, 8, 0)
    #print("scanline x:{} y:{} - start x:{} end x:{} - {}".format(x, y, scan_start, scan_end, SCAN_DATA))
    return data


def coordinateFromPoint(origin, angle, radius):
    xo = origin[0]
    yo = origin[1]

    # Work out the co-ordinate for the pixel on the circumference of the circle
    x = xo - radius * math.cos(math.radians(angle))
    y = yo + radius * math.sin(math.radians(angle))

    # We only want whole numbers
    x = int(round(x))
    y = int(round(y))
    return (x, y)


def scanCircle(image, display_image, point, radius, look_angle):
    x = point[0]
    y = point[1]
    scan_start = x - radius
    scan_end = x + radius
    endpoint_left = coordinateFromPoint(point, look_angle - 90, radius)
    endpoint_right = coordinateFromPoint(point, look_angle + 90, radius)
    # Draw a circle to indicate where we start and end scanning.
    cv2.circle(display_image,
               (endpoint_left[0], endpoint_left[1]), 5, (255, 100, 100), -1, 8, 0)
    cv2.circle(display_image,
               (endpoint_right[0], endpoint_right[1]), 5, (100, 255, 100), -1, 8, 0)
    cv2.line(display_image, (endpoint_left[0], endpoint_left[1]),
             (endpoint_right[0], endpoint_right[1]), (255, 0, 0), 1)
    cv2.circle(display_image, (x, y), radius, (100, 100, 100), 1, 8, 0)

    # We are only going to scan half the circumference
    data = np.zeros(shape=(180, 3))

    # Getting the co-ordinates and value for every degree in the semi circle
    startAngle = look_angle - 90

    returnVal = True
    for i in range(0, 180, 1):
        current_angle = startAngle + i
        scan_point = coordinateFromPoint(point, current_angle, radius)
        if inImageBounds(image, scan_point[0], scan_point[1]):
            imageValue = image[scan_point[1]][scan_point[0]]
            data[i] = [imageValue, scan_point[0], scan_point[1]]
        else:
            returnVal = False
            break

    return returnVal, data


def findInCircle(display_image, scan_data):
    data = np.zeros(shape=(len(scan_data) - 1, 1))
    data[0] = 0
    data[len(data)-1] = 0
    for index in range(1, len(data)):
        data[index] = scan_data[index - 1][0] - scan_data[index][0]

    # left and right should be the boundry values.
    # first element will be the image value
    # second element will be the index of the data item
    left = [0, 0]
    right = [0, 0]

    for index in range(0, len(data)):
        if data[index] > left[1]:
            left[1] = data[index]
            left[0] = index

        if data[index] < right[1]:
            right[1] = data[index]
            right[0] = index

    leftx = int(scan_data[left[0]][1])
    lefty = int(scan_data[left[0]][2])
    lefti = left[0]
    rightx = int(scan_data[right[0]][1])
    righty = int(scan_data[right[0]][2])
    righti = right[0]

    centre_index = int(round((righti + lefti)/2))

    position = [int(scan_data[centre_index][1]),
                int(scan_data[centre_index][2])]

    # mid point, where we believe is the centre of the line
    cv2.circle(display_image,
               (position[0], position[1]), 5, (255, 255, 255), -1, 8, 0)
    # left boundrary dot on the line
    cv2.circle(display_image, (leftx, lefty), 2, (0, 0, 102), 2, 8, 0)
    # right boundrary dot on the line
    cv2.circle(display_image, (rightx, righty), 2, (0, 0, 102), 2, 8, 0)

    return position


def inImageBounds(image, x, y):
    return x >= 0 and y >= 0 and y < len(image) and x < len(image[y])


def findLine(display_image, scan_data, x, y, radius):
    data = np.empty(len(scan_data) - 1)
    data[0] = 0
    data[len(data)-1] = 0
    for index in range(1, len(data)):
        data[index] = scan_data[index - 1] - scan_data[index]

    scan_start = x - radius
    scan_end = x + radius

    left = [0, 0]
    right = [0, 0]

    for index in range(0, len(data)):
        if data[index] > left[1]:
            left[1] = data[index]
            left[0] = index

        if data[index] < right[1]:
            right[1] = data[index]
            right[0] = index

    line_position = (right[0] + left[0]) / 2
    return (scan_start + line_position, y)


def lineAngle(point1, point2):
    angle = round(math.atan2(
        (point2[1] - point1[1]), -(point2[0] - point1[0]))*180/math.pi)
    return angle


def lineLength(point1, point2):
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return int(round(math.sqrt(dx*dx + dy*dy)))


def main():
    direction = "r"
    track = "simple"
    if len(sys.argv) >= 2 and str(sys.argv[1]) == "left":
        direction = "l"
    if len(sys.argv) >= 3 and str(sys.argv[2]) == "hard":
        track = "hard"

    stream = io.BytesIO()
    if DEMO:
        # Create a window
        cv2.namedWindow(WINDOW_DISPLAY_IMAGE)
        # position the window
        cv2.moveWindow(WINDOW_DISPLAY_IMAGE, 0, 35)

    # Open connection to camera
    with picamera.PiCamera() as camera:
        # Set camera resolution
        camera.resolution = (RESOLUTION_X, RESOLUTION_Y)
        # Start loop
        while True:
            mod = 0
            # Get the tick count so we can keep track of performance
            e1 = cv2.getTickCount()
            # Capture image from camera
            camera.capture(stream, format='jpeg', use_video_port=True)
            # Convert image from camera to a numpy array
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            # Decode the numpy array image
            image = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_COLOR)
            # Empty and return the in-memory stream to beginning
            stream.seek(0)
            stream.truncate(0)
            # Create other images
            grey_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            display_image = cv2.copyMakeBorder(
                image, 0, 0, 0, 0, cv2.BORDER_REPLICATE)
            center_point = (SCAN_POS_X, SCAN_HEIGHT)
            if (track == "hard"):
                ret, thresh = cv2.threshold(grey_image, 127, 255, 0)
                thresh = thresh[100:240, 0:320]
                contours_right, hierarchy = cv2.findContours(
                    thresh[0:140, 170:320], cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                contours_left, hierarchy = cv2.findContours(
                    thresh[0:140, 0:150], cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

                # If a interection is detected pull some evasive manouvers
                if len(contours_right) >= 1 and len(contours_left) >= 1:
                    contour_right = max(contours_right, key=cv2.contourArea)
                    contour_left = max(contours_left, key=cv2.contourArea)
                    extent_right = cv2.contourArea(contour_right)
                    extent_left = cv2.contourArea(contour_left)
                    print(extent_left, extent_right)
                    if extent_left >= 21000/5 and extent_right >= 21000/5:
                        print(
                            "More than 2 large contours, most likely an intersection, EVASIVE MANOUVERS !")
                        cv2.rectangle(display_image, (0, 0),
                                      (160, 240), (0, 0, 0), -1)
                        cv2.rectangle(display_image, (0, 0),
                                      (320, 80), (0, 0, 0), -1)
                        cv2.rectangle(grey_image, (0, 0),
                                      (160, 240), (0, 0, 0), -1)
                        cv2.rectangle(grey_image, (0, 0),
                                      (320, 80), (0, 0, 0), -1)
                        mod = -1
                    if DEMO:
                        croppedImg = image.copy()
                        croppedImg_right = croppedImg[100:240, 170:320]
                        croppedImg_left = croppedImg[100:240, 0:150]
                        cv2.drawContours(croppedImg_right,
                                         contours_right, 0, (0, 0, 255), 2)
                        cv2.drawContours(
                            croppedImg_left, contours_left, 0, (0, 255, 0), 2)
                        numpy_horizontal = np.hstack(
                            (croppedImg_left, croppedImg_right))
            else:
                numpy_horizontal = None
            # San a horizontal line based on the centre point
            # We could just use this data to work out how far off centre we are and steer accordingly.
            # Get a data array of all the falues along that line
            # scan_data is an array containing:
            #   - pixel value
            scan_data = scanLine(grey_image, display_image,
                                 center_point, SCAN_RADIUS)
            # The center point we believe the line we are following intersects with our scan line.
            point_on_line = findLine(
                display_image, scan_data, SCAN_POS_X, SCAN_HEIGHT, SCAN_RADIUS)
            # Start scanning the arcs
            # This allows us to look ahead further ahead at the line and work out an angle to steer
            # From the intersection point of the line, scan in an arc to find the line
            # The scan data contains an array
            #   - pixel value
            #   - x co-ordinate
            #   - y co-ordinate
            returnVal, scan_data = scanCircle(
                grey_image, display_image, point_on_line, SCAN_RADIUS_REG, -90)
            previous_point = point_on_line
            # in the same way ads the findLine, go through the data, find the mid point and return the co-ordinates.
            last_point = findInCircle(display_image, scan_data)
            cv2.line(display_image, (previous_point[0], previous_point[1]), (
                last_point[0], last_point[1]), (255, 255, 255), 1)

            actual_number_of_circles = 0
            for scan_count in range(0, NUMBER_OF_CIRCLES + mod):
                returnVal, scan_data = scanCircle(
                    grey_image, display_image, last_point, SCAN_RADIUS_REG, lineAngle(previous_point, last_point))

                # Only work out the next itteration if our point is within the bounds of the image
                if returnVal == True:
                    actual_number_of_circles += 1
                    previous_point = last_point
                    last_point = findInCircle(display_image, scan_data)
                    cv2.line(display_image, (previous_point[0], previous_point[1]), (
                        last_point[0], last_point[1]), (255, 255, 255), 1)
                else:
                    break
            # Draw a line from the centre point to the end point where we last found the line we are following
            cv2.line(display_image, (center_point[0], center_point[1]), (
                last_point[0], last_point[1]), (0, 0, 255), 1)

            # Display the image
            if DEMO:
                cv2.imshow(WINDOW_DISPLAY_IMAGE, display_image)
                if numpy_horizontal is not None:
                    cv2.imshow('Contours', numpy_horizontal)

            # This is the maximum distance the end point of our search for a line can be from the centre point.
            line_scan_length = SCAN_RADIUS_REG * (actual_number_of_circles + 1)
            # This is the measured line length from the centre point
            line_length_from_center = lineLength(center_point, last_point)
            center_y_distance = center_point[1] - last_point[1]
            center_x_distance = center_point[0] - last_point[0]

            # Stop counting all work is done at this point and calculate how we are doing.
            e2 = cv2.getTickCount()
            bearing = lineAngle(center_point, last_point) * -1 - 90
            returnString = "fps {} - bearing {} - x:{} y:{} look distance:{} distance from origin:{}".format(
                1000 / ((e2 - e1)/cv2.getTickFrequency() * 1000),
                bearing,
                center_x_distance,
                center_y_distance,
                line_scan_length,
                line_length_from_center)
            print(returnString)

            if MOVE:
                if mod == -1 and bearing <= 5:
                    print("Derped out on intersection setting bearing to 45 degrees")
                    bearing = 45

                rightSpeed, leftSpeed, pid = move.move(bearing)
            # Wait for ESC to end program
            c = cv2.waitKey(7) % 0x100
            if c == 27:
                break
    cv2.destroyAllWindows()
    return


if __name__ == "__main__":
    main()
