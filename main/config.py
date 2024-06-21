from sensor_modules import *
from action_modules import *
from strategies import *

SENSOR_MODULES = [yolo_sensor, depth_sensor]
ACTION_MODULES = [shotgun_swap, basic_nav]
STRATEGY = basic_strategy
INTERFACE_DATA = [
    5, # num_weapons
    105, # fov
    90, # sensitivity
    (2560, 1440), # aspect_ratio
    0.5, # game_speed
]