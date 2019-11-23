import picamera
import io
import cv2
import numpy as np

with picamera.PiCamera() as camera:
    stream = io.BytesIO()
    camera.resolution = (320, 240)
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
    cv2.imwrite("sample/fork.jpg", grey_image)
