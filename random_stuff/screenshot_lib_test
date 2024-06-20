import time
import dxcam
import dxcam_cpp
from PIL import ImageGrab
import mss

frames = 1000

def test_camera(func, name):
    start_time = time.perf_counter()
    for _ in range(frames):
        image = func()
    end_time = time.perf_counter() - start_time
    print(f"{name} fps: {frames/end_time}")

# Do note:
# For DXCam you should have something constantly changing on your main monitor so that it can capture different frames, otherwise it will output a lower fps
# DXCam testing uses this: https://www.testufo.com/framerates#count=5&background=stars&pps=960

cam1 = dxcam.create()
# Wrapper function because DXCam returns none if a new frame is not yet available
def dxcam1():
    while True:
        frame = cam1.grab()
        if type(frame) != None:
            return frame
test_camera(dxcam1, "DXCam (py)")
cam1.release()

cam2 = dxcam_cpp.create()
# Wrapper function because DXCam returns none if a new frame is not yet available
def dxcam2():
    while True:
        frame = cam2.grab()
        if type(frame) != None:
            return frame
test_camera(dxcam2, "DXCam (cpp)")
cam2.release()

test_camera(ImageGrab.grab, "ImageGrab")

with mss.mss() as sct:
    monitor = sct.monitors[0]
    def mss_grab():
        return sct.grab(monitor)
    test_camera(mss_grab, "MSS")

"""
My testing (On a 165hz 1440p monitor):
DXCam (py) fps: 159.26828328221353
DXCam (cpp) fps: 256.03829841350733
ImageGrab fps: 27.03391855738446
MSS fps: 22.92789913998826

Everything but the DXCams *also* lowered the framerate of the testufo webpage
"""