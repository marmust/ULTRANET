import torchvision.transforms as transforms
import ultra_interface as inter
import torch
import numpy as np
import threading
import numpy as np
import cv2
import time

run_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

net = torch.hub.load("intel-isl/MiDaS", "DPT_Large")
transform = torch.hub.load("intel-isl/MiDaS", "transforms").default_transform

net.to(run_device)

# info that this file returns
wall_right = False
wall_left = False
wall_right_value = 0.0
wall_left_value = 0.0
is_grounded = False
relative_farthest_point = (0, 0)
relative_closest_point = (0, 0)
depth_map = None

# settings of this file
detection_threshold = 0.1
depth_sensor_refreshing = False
threading_loop_speed_limit_time = 0.001

def run_image(image):
    # Convert PIL image to numpy array (OpenCV image)
    cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Run cv2 image through transform
    transformed_image = transform(cv2_image).to(run_device)
    
    # Run transformed image through the network
    with torch.no_grad():
        prediction = net(transformed_image)
    
    # Normalize net output
    prediction -= torch.min(prediction)
    prediction /= torch.max(prediction)
    
    # Convert normalized prediction tensor to PIL image
    to_pil = transforms.ToPILImage()
    pil_output = to_pil(prediction.cpu())
    
    return pil_output

def check_sides(depth_image, threshold=detection_threshold):
    resolution = depth_image.size
    
    # it goes:
    # left
    # upper
    # right
    # lower
    
    # left side crop
    left_side = depth_image.crop((resolution[0] * 0.0,
                                  resolution[1] * 0.4,
                                  resolution[0] * 0.1,
                                  resolution[1] * 0.6))
    
    # right side
    right_side = depth_image.crop((resolution[0] * 0.9,
                                   resolution[1] * 0.4,
                                   resolution[0] * 1.0,
                                   resolution[1] * 0.6))
    
    # bottom (its moved a little to the left to avoid v1's guns)
    bottom_side = depth_image.crop((resolution[0] * 0.4,
                                    resolution[1] * 0.6,
                                    resolution[0] * 0.5,
                                    resolution[1] * 1.0))
    
    # compute avg brightness of each side, then normalize
    left_side_brightness = np.sum(np.array(left_side)) / (left_side.size[0] * left_side.size[1]) / 255
    right_side_brightness = np.sum(np.array(right_side)) / (right_side.size[0] * right_side.size[1]) / 255
    bottom_side_brightness = np.sum(np.array(bottom_side)) / (bottom_side.size[0] * bottom_side.size[1]) / 255
    
    # check if they pass the threshold
    left_side_detected = left_side_brightness > threshold
    right_side_detected = right_side_brightness > threshold
    bottom_side_detected = bottom_side_brightness > threshold
    
    return left_side_brightness, right_side_brightness, left_side_detected, right_side_detected, bottom_side_detected

def depth_loop():
    global wall_left
    global wall_right
    global wall_left_value
    global wall_right_value
    global is_grounded
    global relative_farthest_point
    global relative_closest_point
    global depth_map
    
    # movement PID loop (if in .py, starts when import command is ran)
    while True:
        if depth_sensor_refreshing:
            image = inter.get_game_screenshot()
            depth_map = run_image(image)
            np_depth_map = np.array(depth_map.crop((0, depth_map.size[1] * 0.4, depth_map.size[0], depth_map.size[1] * 0.6)))
            
            # use some voodoo to calculate x, y coodrinates (on screen) of darkest and brightest pixel
            relative_farthest_point = np.unravel_index(np.argmin(np_depth_map), np_depth_map.shape)
            relative_closest_point = np.unravel_index(np.argmax(np_depth_map), np_depth_map.shape)
            
            # calculate and update surroundings
            wall_left_value, wall_right_value, wall_left, wall_right, is_grounded = check_sides(depth_map)
        else:
            time.sleep(threading_loop_speed_limit_time)

# put movement loop on different thread
movement_thread = threading.Thread(target=depth_loop)
movement_thread.start()
print(f"{__name__}   --->   started depth_sensor thread succesfully (stop from task manager)")