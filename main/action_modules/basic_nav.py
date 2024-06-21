from .base_action_module import action_module
import time
import torch as pyt

RELEVEL_TIMEOUT = 5 # Basically if the nav module hasn't been used in 5 seconds, recenter the camera
CORNER_THRESHOLD = 0.1

class basic_nav(action_module):
    
    required_sensors = ["depth_sensor"]

    def __init__(self, interface):
        super().__init__(interface)
        self.previous_depthmap = None
        self.previous_time = time.time()
    
    def run(self, depth_data):

        wall_left, wall_right, floor, depth_map = depth_data
        current_time = time.time()

        if current_time - self.previous_time > RELEVEL_TIMEOUT: # It's been too long since the nav was last used, make sure to level the camera
            self.previous_depthmap = None
            self.interface.apply_rotation(0, 1)
            time.sleep(0.38 / self.interface.sensitivity / 100 / self.interface.game_speed)
            self.interface.apply_rotation(0, -1)
            time.sleep(0.17 / self.interface.sensitivity / 100 / self.interface.game_speed)
        
        if not self.previous_depthmap is None:
            difference = pyt.sum(pyt.abs(depth_map - self.previous_depthmap)) / pyt.numel(depth_map) / 255
            if difference > CORNER_THRESHOLD:
                self.interface.apply_rotation(1, 0)
                time.sleep(0.1)
            else:
                direction = wall_left - wall_right
                self.interface.apply_movement(direction, 1)
                self.interface.apply_rotation(direction * 0.5, 0)
        else:
            direction = wall_left - wall_right
            self.interface.apply_movement(direction, 1)
            self.interface.apply_rotation(direction * 0.5, 0)
        
        self.previous_depthmap = depth_map