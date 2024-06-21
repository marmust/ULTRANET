import vgamepad as vg
import dxcam_cpp as dx
import time
import numpy as np
import cv2

MIN_DURATION = 0.001 # The minimum duration to do button presses for actions, should be the lowest that the game can possibly detect but I'm not going to spend a lot of time optimizing it (yet)
IMAGE_RESIZE = True # Whether to resize the image for all sensors (downscale or upscale, either one)
RESIZE_DIMS = (640, 480) # The scale to resize the image to (default 480p for the yolov5m model)
RESIZE_INTERP_TYPE = cv2.INTER_LINEAR # The type of interpolation to apply when resizing the image (default cv2's default interpolation type)

class ultrakill_interface():

    """
    A class to interface with ultrakill
    Needs the fov, sensitivity, aspect ratio, and game speed
    Implements methods to both control the game and get the current screen
    """

    def __init__(self, num_weapons, fov, sensitivity, aspect_ratio, game_speed):
        # Variables to keep track of a buncha stuff (assumes standard weapon order, starting on the piercer revolver)
        self.gamepad = vg.VX360Gamepad()
        self.current_weapon = 0
        self.current_variant = 0
        self.num_of_weapons = 5
        self.current_arm = 0
        self.fov = fov
        self.sensitivity = sensitivity
        self.aspect_ratio = aspect_ratio
        self.game_speed = game_speed
        self.num_weapons = num_weapons
        self.cam = dx.create()
    
    # Rotates the camera (right stick)
    def apply_rotation(self, x, y):
        self.gamepad.right_joystick_float(x_value_float=x, y_value_float=y)
        self.gamepad.update()

    # Moves v1 (left stick)
    def apply_movement(self, x, y):
        self.gamepad.left_joystick_float(x_value_float=x, y_value_float=y)
        self.gamepad.update()

    # Jump (A press)
    def jump(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self.gamepad.update()

    # Dash (left stick press)
    def dash(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        self.gamepad.update()

    # Start holding slide/slam (right stick press)
    def slide_start(self):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
        self.gamepad.update()

    # Stop holding slide/slam (right stick release)
    def slide_end(self):
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
        self.gamepad.update()

    # Taps main fire for duration seconds (right trigger)
    def main_fire_tap(self, duration = MIN_DURATION):
        self.gamepad.right_trigger_float(value_float=1)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.right_trigger_float(value_float=0)
        self.gamepad.update()

    # Presses down main fire (right trigger)
    def main_fire_press(self):
        self.gamepad.right_trigger_float(value_float=1)
        self.gamepad.update()

    # Releases main fire (right trigger)
    def main_fire_release(self):
        self.gamepad.right_trigger_float(value_float=0)
        self.gamepad.update()

    # Taps alt fire for duration seconds (left trigger)
    def alt_fire_tap(self, duration = MIN_DURATION):
        self.gamepad.left_trigger_float(value_float=1)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.left_trigger_float(value_float=0)
        self.gamepad.update()

    # Presses down alt fire (left trigger)
    def alt_fire_press(self):
        self.gamepad.left_trigger_float(value_float=1)
        self.gamepad.update()

    # Releases alt fire (left trigger)
    def alt_fire_release(self):
        self.gamepad.left_trigger_float(value_float=0)
        self.gamepad.update()

    # Punches for specified duration (X button)
    def punch(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        self.gamepad.update()

    # Switches weapons, 1 for up, -1 for down
    def switch_weapon(self, direction, duration = MIN_DURATION):
        if direction == -1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            self.gamepad.update()
            time.sleep(duration)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            self.gamepad.update()
        elif direction == 1:
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            self.gamepad.update()
            time.sleep(duration)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            self.gamepad.update()
        self.current_weapon = (self.current_weapon + direction) % self.num_weapons
        if self.current_weapon == -1:
            self.current_weapon = self.num_weapons - 1

    # Switches the weapon to a specific index
    def switch_weapon_to(self, weapon_idx):
        if weapon_idx > self.current_weapon: # Current weapon is too low of an index, scroll up weapons till it reaches the desired one
            for _ in range(weapon_idx - self.current_weapon):
                self.switch_weapon(1)
        if weapon_idx < self.current_weapon: # Current weapon is too high of an index, scroll down weapons till it reaches the desired one
            for _ in range(self.current_weapon - weapon_idx):
                self.switch_weapon(-1)
    
    # Switches the weapon variation up by one
    def switch_variation(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        self.gamepad.update()
        self.current_variant = (self.current_variant + 1) % 3

    # Switches the weapon variation to a specific index
    def switch_variation_to(self, variation):
        while variation != self.current_variant:
            self.switch_variation()

    def switch_fist_variation(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        self.gamepad.update()
        self.current_arm = (self.current_arm + 1) % 2

    # Holds down whiplash for duration seconds
    def whiplash(self, duration = MIN_DURATION):
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        self.gamepad.update()
        time.sleep(duration)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        self.gamepad.update()

    # Resets the level (I'm not touching this and assuming it works)
    def reset_level(self):
        # restart level
        # open settings
        self.gamepad.reset()
        self.gamepad.update()
        
        self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        self.gamepad.update()
        
        time.sleep(0.1)
        
        # go down to checkpoint button
        # go down to restart button
        for _ in range(2):
            self.gamepad.left_joystick_float(x_value_float=0, y_value_float=-1)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.reset()
            self.gamepad.update()
            time.sleep(0.1)
        
        # click the restart button
        # click a again to confirm restart
        for _ in range(2):
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.reset()
            self.gamepad.update()
            time.sleep(0.1)

    # Take a screenshot (uses dxcam)
    def get_game_screenshot(self):
        screenshot = self.cam.grab()
        while screenshot is None:
            screenshot = self.cam.grab()
        if IMAGE_RESIZE:
            screenshot = cv2.resize(screenshot, RESIZE_DIMS, interpolation=RESIZE_INTERP_TYPE) # Use cv2 here for fast easy resizing for interpolation
        return screenshot