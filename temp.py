import picamera
import cv2
import numpy as np
import io

with picamera.PiCamera() as camera:
    # Set camera resolution
    camera.resolution = (320, 240)
    # Start loop
    while True:
        stream = io.BytesIO()
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
        cv2.imwrite('demo.jpg', grey_image)
