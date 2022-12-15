# import the opencv library
import cv2 # pip3 install opencv-python
import imutils
import numpy as np
import numpy

preview = None

class CameraHandler:

    def initCamera():
        global preview
        preview = False
        camera = cv2.VideoCapture(0)
        return camera

    def closeCamera(camera):
        camera.release()

    def getFrame(camera):
        ret, frame = camera.read()
        # frame = cv2.resize(frame, (640, 360))
        frame = imutils.resize(frame, height=720)
        frame = imutils.rotate(frame, 180)
        if preview == True:
            cv2.imshow("frame",frame)
        # OpenCV Requirements
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass
        return frame

def main():
    # Parameters
    camera = None
    frame1 = None
    frame2 = None
    motion = None
    percentage = None
    # Camera Start
    camera = CameraHandler.initCamera()
    while(True):
        frame = CameraHandler.getFrame(camera)
    CameraHandler.closeCamera(camera)

if __name__ == '__main__':
    main()
