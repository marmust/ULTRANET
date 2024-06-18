# this file hadnles all communication with ultrakill

import vgamepad as vg
from PIL import ImageGrab
import time
import math

gamepad = vg.VX360Gamepad()

# these variables keep track of v1's current weapon combination
current_weapon = 0
num_of_weapons = 5
current_arm = "blue"
    
# handles v1's head rotation (mouse movement alternative)
def apply_rotation(x_rotation, y_rotation):
    # apply rotation
    gamepad.right_joystick_float(x_value_float=x_rotation, y_value_float=y_rotation)
    gamepad.update()

# alternative for W / A / S / D movement
def apply_movement(x_movement, y_movement):
    # move back / fourth / left / right
    gamepad.left_joystick_float(x_value_float=x_movement, y_value_float=y_movement)
    gamepad.update()

# rotates towards a specified point in the screenshot
def rotate_to_point(norm_x, norm_y, fov, sensitivity, norm_aspect_ratio, game_speed):
    ######################################################################################################################
    # if you fully twist joystick for 1 sec, how many degrees will v1 rotate                                             #
    max_rotation_per_second_degrees = 360 / 0.67 * (sensitivity / 100)                                                   #
                                                                                                                         #
    # if its equal to zero it will become 0.001 (to avoid division by zero errors)                                       #
    norm_x += (abs(norm_x) <= 0.001) / 100                                                                               #
    norm_y += (abs(norm_y) <= 0.001) / 100                                                                               #
                                                                                                                         #
    # number of degrees offset from crosshair                                                                            #
    x_degrees = norm_x * fov                                                                                             #----- math
    y_degrees = norm_y * fov                                                                                             #
                                                                                                                         #
    # convert normx and normy to "sign only" format to use as stick input (also account screen aspect ratio):            #
    norm_x = (abs(norm_x) * norm_x) / (norm_x * norm_x) * norm_aspect_ratio[0]                                           #
    norm_y = (abs(norm_y) * norm_y) / (norm_y * norm_y) * norm_aspect_ratio[1]                                           #
                                                                                                                         #
    # the time that the rotation needs to be applied until the target is in crosshair                                    #
    allignment_time = max(abs(x_degrees), abs(y_degrees)) / max_rotation_per_second_degrees                              #
    ######################################################################################################################
    
    apply_rotation(norm_x, norm_y)
    time.sleep(allignment_time * 1 / (game_speed / 100))
    apply_rotation(0, 0)

# click jump
def jump(press_duration):
    # click (A) really fast
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()

# click dash
def dash(press_duration):
    # click on left joystick really fast
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()

# hold down the equivalent of the CTRL key
def slam_and_slide_start():
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
    gamepad.update()

# release the equivalent of the CTRL key
def slam_and_slide_end():
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
    gamepad.update()

# click and release equivalent of main fire really quickly (for exmample railcanon)
def shoot_main_tap(start_delay, press_duration):
    time.sleep(start_delay)
    gamepad.right_trigger_float(value_float=1)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.right_trigger_float(value_float=0)
    gamepad.update()

# hold down shoot key until is released (for example when shooting nailgun)
def shoot_main_hold():
    gamepad.right_trigger_float(value_float=1)
    gamepad.update()
def shoot_main_release():
    gamepad.right_trigger_float(value_float=0)
    gamepad.update()

# same 3 functions for alt fire
def shoot_alt_tap(press_duration):
    gamepad.left_trigger_float(value_float=1)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.left_trigger_float(value_float=0)
    gamepad.update()

def shoot_alt_hold():
    gamepad.left_trigger_float(value_float=1)
    gamepad.update()

def shoot_alt_release():
    gamepad.left_trigger_float(value_float=0)
    gamepad.update()

# holds down punch button for specified duration
def punch(press_duration):
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    gamepad.update()

# equivalent of scrolling down 1 tick to switch weapon
def switch_weapon_down(press_duration):
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
    current_weapon = (current_weapon - 1) % num_of_weapons

# same thing here just scroll the opposite way
def switch_weapon_up(press_duration):
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    current_weapon = (current_weapon + 1) % num_of_weapons

def switch_weapon_to(weapon_idx):
    while current_weapon != weapon_idx:
        switch_weapon_up()

# this switches the weapon "type" forward once
def switch_weapon_color(press_duration):
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
    gamepad.update()
    time.sleep(press_duration)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
    gamepad.update()

# hold down the whiplash button for [duration] seconds
def whiplash(press_duration):
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
    gamepad.update()
    time.sleep(press_duration / 2)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
    gamepad.update()
    time.sleep(press_duration / 2)

def reset_level():
    # restart level
    # open settings
    gamepad.reset()
    gamepad.update()
    
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    gamepad.update()
    
    time.sleep(0.1)
    
    # go down to checkpoint button
    # go down to restart button
    for _ in range(2):
        gamepad.left_joystick_float(x_value_float=0, y_value_float=-1)
        gamepad.update()
        time.sleep(0.1)
        gamepad.reset()
        gamepad.update()
        time.sleep(0.1)
    
    # click the restart button
    # click a again to confirm restart
    for _ in range(2):
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(0.1)
        gamepad.reset()
        gamepad.update()
        time.sleep(0.1)

# util func to take a screenshot of the screen
def get_game_screenshot():
    screenshot = ImageGrab.grab()
    # temp (keep 16x9 ratio)
    #screenshot = screenshot.resize((1024, 576))
    return screenshot

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