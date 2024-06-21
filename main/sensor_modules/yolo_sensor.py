from .base_sensor_module import sensor_module
import torch as pyt
import os
import sys

CONFIDENCE_THRESHOLD = 0.5
DEBUG = False

if DEBUG:
    import cv2
    import numpy as np

class yolo_sensor(sensor_module):

    def __init__(self):

        # Load in the model and send it to the appropriate device
        path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.net = pyt.hub.load("ultralytics/yolov5", "custom", path=path+"//model_weights//6_class_original_yolov5m.pt").to(pyt.device("cuda" if pyt.cuda.is_available() else "cpu"))
        self.net_result = None
        self.filtered_net_result = None

    @pyt.no_grad
    def run(self, image):
        self.net_result = self.net(image) # Run the image net on the image to find boxes
        self.filtered_net_result = self.net_result.xywhn[0][self.net_result.xywhn[0][:, -2] > CONFIDENCE_THRESHOLD] # Filter the net's results to only include boxes over a certain confidence level
        if DEBUG:
            print(self.filtered_net_result)
            image = np.array(self.net_result.render())[0]
            cv2.imshow("test", image)
            cv2.waitKey()
        return self.filtered_net_result # Return the filtered net result