from .base_sensor_module import sensor_module
import torch as pyt

# Detection threshold for brightness
DETECTION_THRESHOLD = 0.1

# Adjust these as needed, defined as [Left, Right, Top, Bottom]
LEFT_CROP_RATIO = [0.0, 0.1, 0.4, 0.6]
RIGHT_CROP_RATIO = [0.9, 1.0, 0.4, 0.6]
BOTTOM_CROP_RATIO = [0.4, 0.5, 0.6, 1.0]

class depth_sensor(sensor_module):

    def __init__(self):

        # Load in model and transform
        self.device = pyt.device("cuda" if pyt.cuda.is_available() else "cpu")
        self.net = pyt.hub.load("intel-isl/MiDaS", "DPT_Large").to(self.device)
        self.transform = pyt.hub.load("intel-isl/MiDaS", "transforms").default_transform

        # Keep track of these because why not
        self.wall_left = False
        self.wall_right = False
        self.floor = False
        self.left_brightness = 0.0
        self.right_brightness = 0.0
        self.bottom_brightness = 0.0
        self.depth_map = None
    
    @pyt.no_grad
    def run(self, image):

        # Transform the image and run the model on it
        transformed_image = self.transform(image).to(self.device)
        self.depth_map = self.net(transformed_image)

        # Normalize the depth map
        self.depth_map -= pyt.min(self.depth_map)
        self.depth_map /= pyt.max(self.depth_map)

        # Pull out the sides using the crop ratios
        shape = list(self.depth_map.shape)
        left_side = self.depth_map[pyt.arange(LEFT_CROP_RATIO[0]*shape[0], LEFT_CROP_RATIO[1]*shape[0], dtype=pyt.int8), pyt.arange(LEFT_CROP_RATIO[2]*shape[1], LEFT_CROP_RATIO[3]*shape[1], dtype=pyt.int8), :]
        right_side = self.depth_map[pyt.arange(RIGHT_CROP_RATIO[0]*shape[0], RIGHT_CROP_RATIO[1]*shape[0], dtype=pyt.int8), pyt.arange(RIGHT_CROP_RATIO[2]*shape[1], RIGHT_CROP_RATIO[3]*shape[1], dtype=pyt.int8), :]
        bottom = self.depth_map[pyt.arange(BOTTOM_CROP_RATIO[0]*shape[0], BOTTOM_CROP_RATIO[1]*shape[0], dtype=pyt.int8), pyt.arange(BOTTOM_CROP_RATIO[2]*shape[1], BOTTOM_CROP_RATIO[3]*shape[1], dtype=pyt.int8), :]
        
        # Find the approx. brightness for each side
        self.left_brightness = pyt.sum(left_side / pyt.numel(left_side)).item() / 255
        self.right_brightness = pyt.sum(right_side / pyt.numel(right_side)).item() / 255
        self.bottom_brightness = pyt.sum(bottom / pyt.numel(bottom)).item() / 255

        # If the brightness is above the threshold, there is something there
        self.wall_left = self.left_brightness > DETECTION_THRESHOLD
        self.wall_right = self.right_brightness > DETECTION_THRESHOLD
        self.floor = self.bottom_brightness > DETECTION_THRESHOLD

        return self.wall_left, self.wall_right, self.floor, self.depth_map