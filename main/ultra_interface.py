import vgamepad as vg
import dxcam_cpp as dx
import time
import numpy as np

MIN_DURATION = 0.001

class Ultrakill_Interface():

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

    # Rotates towards a specified point on the screen
    def rotate_to_point(self, x, y):

        # Approximate the degrees to rotate with the screen aspect ratio and fov
        x_degrees = x * self.fov / self.aspect_ratio[0]
        y_degrees = y * self.fov / self.aspect_ratio[1]

        # Time to apply rotation until the target is on crosshair
        allignment_time_x = abs(x_degrees) / self.sensitivity
        allignment_time_y = abs(y_degrees) / self.sensitivity

        if allignment_time_x < allignment_time_y: # Less time to travel on X
            self.apply_rotation(np.sign(x), np.sign(y))
            time.sleep(allignment_time_x / self.game_speed) # Rotate until X is correct
            self.apply_rotation(0, np.sign(y)) # X is aligned, no need to rotate on it
            time.sleep((allignment_time_y - allignment_time_x) / self.game_speed) # Rotate until the Y is correct as well
        else: # Less time to travel on Y
            self.apply_rotation(np.sign(x), np.sign(y))
            time.sleep(allignment_time_y / self.game_speed) # Rotate until Y is correct
            self.apply_rotation(np.sign(x), 0) # Y is aligned, no need to rotate on it
            time.sleep((allignment_time_x - allignment_time_y) / self.game_speed) # Rotate until the X is correct as well

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
        current_weapon = (current_weapon + direction) % self.num_weapons
        if current_weapon == -1:
            current_weapon = self.num_weapons - 1

    # Switches the weapon to a specific index
    def switch_weapon_to(self, weapon_idx):
        if weapon_idx < self.current_weapon: # Current weapon is too low of an index, scroll up weapons till it reaches the desired one
            for _ in range(self.current_weapon - weapon_idx):
                self.switch_weapon(1)
        if weapon_idx > self.current_weapon: # Current weapon is too high of an index, scroll down weapons till it reaches the desired one
            for _ in range(weapon_idx - self.current_weapon):
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
        while type(screenshot) == None:
            screenshot = self.cam.grab()
        return screenshot


"""
# ill call this part: ---HIGH LEVEL OPERATIONS---

# function to change the color of the shotgun with the *perfect timing
def shotgun_swaps_thread_function(game_speed):
    while True:
        switch_weapon_color(0.1)
        time.sleep(0.45 * (1 / (game_speed / 100)))

# if applied to rotation, camera will zigzag abck and fourth
def get_zigzag_direction(relative_zigzag_time, sensitivity, game_speed):
    sensitivity = sensitivity / 100
    relative_zigzag_time *= 1 / (game_speed / 100)
    relative_zigzag_time = relative_zigzag_time / sensitivity
    # skibidi toilet line
    return float(time.time() % relative_zigzag_time > (relative_zigzag_time / 2)) * 2 - 1

# make it so v1 is looking straight forward no matter what
def level_horizon(sensitivity, game_speed):
    # normalize sensitivity
    sensitivity = sensitivity / 100
    
    # look up until v1 is definatly facing 90 degrees up
    apply_rotation(0, 1)
    time.sleep(0.38 / sensitivity * 1 / (game_speed / 100))
    # look back down until v1 is looking at the horizon (based on sensitivity)
    apply_rotation(0, -1)
    time.sleep(0.17 / sensitivity * 1 / (game_speed / 100))
    apply_rotation(0, 0)
"""