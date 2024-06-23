from sensor_modules import *
from action_modules import *
from strategies import *

SENSOR_MODULES = [yolo_sensor, depth_sensor]
ACTION_MODULES = [shotgun_swap, basic_nav]
STRATEGY = basic_strategy
INTERFACE_DATA = [
    105, # fov
    50, # sensitivity
    (2560, 1440), # aspect_ratio
    1, # game_speed
]