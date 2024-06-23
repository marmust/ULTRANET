import dxcam_cpp as dx
import time
import cv2
from inputs import *

MIN_DURATION = 0 # The minimum duration to do button presses for actions, should be the lowest that the game can possibly detect but I'm not going to spend a lot of time optimizing it (yet)
IMAGE_RESIZE = True # Whether to resize the image for all sensors (downscale or upscale, either one)
RESIZE_DIMS = (640, 480) # The scale to resize the image to (default 480p for the yolov5m model)
RESIZE_INTERP_TYPE = cv2.INTER_LINEAR # The type of interpolation to apply when resizing the image (default cv2's default interpolation type)

class ultrakill_interface():

    """
    A class to interface with ultrakill
    Needs the fov, sensitivity, aspect ratio, and game speed
    Implements methods to both control the game and get the current screen
    """

    def __init__(self, fov, sensitivity, aspect_ratio, game_speed):
        # Variables to keep track of a buncha stuff (assumes standard weapon order, starting on the piercer revolver)
        self.inp_man = input_manager()
        self.current_weapon = 0
        self.current_variant = 0
        self.num_of_weapons = 5
        self.current_arm = 0
        self.fov = fov
        self.sensitivity = sensitivity
        self.aspect_ratio = aspect_ratio
        self.game_speed = game_speed
        self.cam = dx.create()
    
    # Levels the camera out by looking up to the sky and down halfway immediately
    def level_camera(self):
        self.apply_rotation(0, self.aspect_ratio[1]/self.sensitivity)
        self.apply_rotation(0, -0.5*self.aspect_ratio[1]/self.sensitivity)

    # Rotates the camera
    def apply_rotation(self, x, y):
        self.inp_man.move_mouse(int(x), int(y))

    # Move forwards/backwards right/left
    def apply_movement(self, forwards = 0, right = 0):
        if forwards == 1: # Press W and release S
            self.inp_man.press_key("W")
            self.inp_man.release_key("S")
        elif forwards == -1: # Press S and release W
            self.inp_man.press_key("S")
            self.inp_man.release_key("W")
        else: # No forwards/backwards movement, release both keys
            self.inp_man.release_key("W")
            self.inp_man.release_key("S")
        if right == 1: # Press D and release A
            self.inp_man.press_key("D")
            self.inp_man.release_key("A")
        elif right == -1: # Press A and release D
            self.inp_man.press_key("A")
            self.inp_man.release_key("D")
        else: # No sideways movement, release both keys
            self.inp_man.release_key("D")
            self.inp_man.release_key("A")

    # Jump
    def jump(self, duration = MIN_DURATION):
        self.inp_man.tap_key("Space", duration)

    # Dash
    def dash(self, duration = MIN_DURATION):
        self.inp_man.tap_key("Shift", duration)

    # Start holding slide/slam
    def slide_start(self):
        self.inp_man.press_key("Ctrl")

    # Stop holding slide/slam
    def slide_end(self):
        self.inp_man.release_key("Ctrl")

    # Taps main fire for duration seconds
    def main_fire_tap(self, duration = MIN_DURATION):
        self.inp_man.click(True, duration)

    # Presses down main fire
    def main_fire_press(self):
        self.inp_man.mouse_down(True)

    # Releases main fire
    def main_fire_release(self):
        self.inp_man.mouse_up(True)

    # Taps alt fire for duration seconds
    def alt_fire_tap(self, duration = MIN_DURATION):
        self.inp_man.click(False, duration)

    # Presses down alt fire
    def alt_fire_press(self):
        self.inp_man.mouse_down(False)

    # Releases alt fire
    def alt_fire_release(self):
        self.inp_man.mouse_up(False)

    # Punches for specified duration
    def punch(self, duration = MIN_DURATION):
        self.inp_man.tap_key("F", duration)

    # Switches the weapon to a specific index
    def switch_weapon_to(self, weapon_idx):
        self.inp_man.tap_key(str(weapon_idx+1))
        self.current_weapon = weapon_idx
        self.current_variant = 0
    
    # Switches the weapon variation up by one
    def switch_variation_up(self):
        self.inp_man.tap_key("E")
        self.current_variant = (self.current_variant + 1) % 3

    # Switches the weapon variation down by one
    def switch_variation_down(self):
        self.inp_man.tap_key("Q")
        self.current_variant = self.current_variant - 1
        if self.current_variant == -1:
            self.current_variant = 2

    # Switches the weapon variation to a specific index
    def switch_variation_to(self, variation):
        diff = variation - self.current_variant
        if diff == 0:
            return
        elif diff == 1 or diff == -2:
            self.switch_variation_up()
        elif diff == -1 or diff == 2:
            self.switch_variation_down()

    def switch_fist_variation(self):
        self.inp_man.tap_key("G")
        self.current_arm = (self.current_arm + 1) % 2

    # Holds down whiplash for duration seconds
    def whiplash(self, duration = MIN_DURATION):
        self.inp_man.tap_key("R", duration)

    # Take a screenshot (uses dxcam)
    def get_game_screenshot(self):
        screenshot = self.cam.grab()
        while screenshot is None:
            screenshot = self.cam.grab()
        if IMAGE_RESIZE:
            screenshot = cv2.resize(screenshot, RESIZE_DIMS, interpolation=RESIZE_INTERP_TYPE) # Use cv2 here for fast easy resizing for interpolation
        return screenshot