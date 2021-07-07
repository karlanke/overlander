import pathlib
import cv2
import time

path = pathlib.Path(__file__).parent.absolute()


class MockCamera:

    def read(self):
        temp_vid = cv2.VideoCapture(f'{path}/static/there-is-no-connected-camera-mac.jpg')

        ret, frame = temp_vid.read()

        temp_vid.release()

        time.sleep(0.2)

        return ret, frame

    def release(self):
        pass
