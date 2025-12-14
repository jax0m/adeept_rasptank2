#!/usr/bin/env python
import os
import threading
import picamera2
import cv2  # We'll need this for converting frames to JPEG
import time
import flask
import flask_cors
from flask import Response

app = flask.Flask(__name__)
flask_cors.CORS(app, supports_credentials=True)


# Create a custom camera class that uses picamera2
class Picamera2Stream:
    def __init__(self):
        self.camera = picamera2.Picamera2()
        self.config = self.camera.create_video_configuration(main={"size": (640, 480)})
        self.camera.configure(self.config)
        self.camera.start()
        self.frame = None
        self.capture_thread = None
        self.running = True

        # Start the capture thread
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.capture_thread.start()

    def capture_frames(self):
        while self.running:
            try:
                # Get the latest frame
                self.frame = self.camera.capture_array()
                # time.sleep(0.01)  # Small delay to avoid overloading
            except Exception as e:
                print(f"Error capturing frame: {e}")
                self.running = False

    def stop(self):
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        if self.camera:
            self.camera.stop()

    def get_frame(self):
        """Get the most recent frame converted to JPEG"""
        if self.frame is None:
            return None

        # Convert frame to BGR for OpenCV
        frame_bgr = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

        # Convert to JPEG
        _, buffer = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return buffer.tobytes()


# Create our camera instance
camera = Picamera2Stream()


def gen():
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        time.sleep(0.1)  # Small delay to avoid overloading the CPU


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


# The rest of your code for serving static files remains the same
dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route("/api/img/<path:filename>")
def sendimg(filename):
    return flask.send_from_directory(dir_path + "/dist/img", filename)


@app.route("/js/<path:filename>")
def sendjs(filename):
    return flask.send_from_directory(dir_path + "/dist/js", filename)


@app.route("/css/<path:filename>")
def sendcss(filename):
    return flask.send_from_directory(dir_path + "/dist/css", filename)


@app.route("/api/img/icon/<path:filename>")
def sendicon(filename):
    return flask.send_from_directory(dir_path + "/dist/img/icon", filename)


@app.route("/fonts/<path:filename>")
def sendfonts(filename):
    return flask.send_from_directory(dir_path + "/dist/fonts", filename)


@app.route("/<path:filename>")
def sendgen(filename):
    return flask.send_from_directory(dir_path + "/dist", filename)


@app.route("/")
def index():
    return flask.send_from_directory(dir_path + "/dist", "index.html")


class webapp:
    def __init__(self):
        self.camera = camera

    def modeselect(self, modeInput):
        # This would need to be implemented based on your requirements
        print(f"Mode selected: {modeInput}")

    def colorFindSet(self, H, S, V):
        # This would need to be implemented based on your requirements
        print(f"Color set: H={H}, S={S}, V={V}")

    def thread(self):
        app.run(host="0.0.0.0", port=5000, threaded=True)

    def startthread(self):
        fps_threading = threading.Thread(target=self.thread)
        fps_threading.daemon = False
        fps_threading.start()


if __name__ == "__main__":
    WEB = webapp()
    try:
        WEB.startthread()
    except Exception as e:
        print(f"Error: {e}")
        camera.stop()
        print("exit")
