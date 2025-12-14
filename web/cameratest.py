#!/usr/bin/python3

import time

from picamera2 import Picamera2

picam2 = Picamera2()

# Configure for still image capture (no preview)
config = picam2.create_still_configuration(main={"size": (1640, 1232)})
picam2.configure(config)

# Start the camera
picam2.start()
time.sleep(2)  # Allow time for camera to stabilize

# Capture image directly to file
metadata = picam2.capture_file("test2.jpg")
print(metadata)

picam2.close()
