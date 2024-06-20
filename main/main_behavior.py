from sensors import depth_sensor as depth
from sensors import targeting_sensor as targeting
import ultra_interface as inter
import threading
import numpy as np
import time

# behaviour settings:
level_horizon_seconds = 5 # default: 5
quick_scan_enter_delay = 1 # default: 1
remain_in_search_mode_seconds = 4 # default: 4

# ULTRAKILL settings:
in_game_sensitivity = 100 # default: 100
in_game_fov = 140 # default: 140
normalized_screen_aspect_ratio = (1, 0.5625) # default: (1, 0.5625) which is 16:9
in_game_speed = 50 # default: 50

# settings settings:
threading_loop_speed_limit_time = 0.0001 # default: 0.0001

# backend vars
unused_targeting_data_available = False

# when fresh data from the targeting script is available, switch the "semaphore-like"
def recieve_fresh_targeting_update():
    global unused_targeting_data_available
    unused_targeting_data_available = True

# like threadripper you get it?
def whiplash_thread_wrapper(press_duration):
    mini_thread = threading.Thread(target=inter.whiplash, args=(press_duration,))
    mini_thread.start()
    mini_thread.join()

# function that holds the main loop that manages the ai's behaviour
def main_behaviour():
    global unused_targeting_data_available
    
    # thread that swaps shotgun colors in sync for shotgun swaps
    shotgun_thread = threading.Thread(target=inter.shotgun_swaps_thread_function, args=(in_game_speed,))
    shotgun_thread.start()
    
    # take initial screenshot (mostly to not have this variable as None)
    current_img = inter.get_game_screenshot()
    
    # internal loop variables init
    target_locked_flag = False
    loop_start_time = time.time()
    last_horizon_level_time = loop_start_time
    last_target_detection_time = loop_start_time
    
    while True:
        loop_current_time = time.time()
        
        # all behaviour entry / exit conditions:
        targets_detected = bool(targeting.are_targets_detected)
        target_locked = bool(targeting.is_target_locked)
        quick_scan_active = loop_current_time < last_target_detection_time + remain_in_search_mode_seconds
        
        # mode 1: targets detected! that means were in combat mode
        if targets_detected:
            depth.depth_sensor_refreshing = False
        
            last_target_detection_time = loop_current_time
            
            # area taken on screen by the biggest target (normalized)
            biggest_target_area = max(targeting.all_target_sizes_list)
            
            # use to rotate, then mark the current data as used
            if unused_targeting_data_available:
                inter.rotate_to_point(float(targeting.chosen_target_norm_position[0]),
                                      float(targeting.chosen_target_norm_position[1]) * -1,
                                      in_game_fov,
                                      in_game_sensitivity,
                                      normalized_screen_aspect_ratio,
                                      in_game_speed)
                
                unused_targeting_data_available = False
            
            # start shotgun swapping
            inter.shoot_main_hold()
            
            # whiplash if closest enemy is really far
            if biggest_target_area < 0.001:
                whiplash_thread_wrapper(0.3)
            
            # drunk wabble right and left, while keeping a certain distance with the enemy
            inter.apply_movement(inter.get_zigzag_direction(2, 100, in_game_speed),
                                 (not biggest_target_area > 0.03) * 2 - 1)
            
            # dodge potential attack if enemy is too close (backwards bcs command above)
            if biggest_target_area > 0.05:
                inter.dash(0.01)
            
            time.sleep(threading_loop_speed_limit_time)
           
        # mode 2: no targets are no longer visible, zigzag v1's head to find enemies that might be outside the field of view for 8 seconds
        if quick_scan_active and not targets_detected and loop_current_time > last_target_detection_time + quick_scan_enter_delay:
            # scanning mode 1: refind target - we rotate in teh direction that the target used to be while zigzagging
            inter.shoot_main_release()
            inter.apply_rotation(max(1, min(-1, float(targeting.chosen_target_norm_position[0]) * 5)),
                                 inter.get_zigzag_direction(1, in_game_sensitivity, in_game_speed))
            
            time.sleep(threading_loop_speed_limit_time)
        
        # mode 3: we didnt find any enemies even after 8 seconds of doing the zigzagging, navigate the environment.
        while not loop_current_time < last_target_detection_time + remain_in_search_mode_seconds and not targeting.are_targets_detected:
            depth.depth_sensor_refreshing = True
            
            # get the two images to be compared
            previous_img = current_img
            current_img = inter.get_game_screenshot()
            
            previous_nparray = np.array(previous_img)
            current_nparray = np.array(current_img)
            
            # calculate how different the images are (normalized difference)
            difference = np.sum(np.abs(previous_img - current_nparray)) / 255 / np.prod(previous_nparray.shape)
            
            # check if stuck in corner (probably)
            if difference < 0.1:
                inter.apply_rotation(inter.get_zigzag_direction(20, in_game_sensitivity, in_game_speed), 0)
                inter.apply_movement(0, -1)
                time.sleep(0.1)
            else:
                # else use normal movement
                inter.apply_movement(bool(depth.wall_left) - bool(depth.wall_right), 1)
                depth_steering_direction = bool(depth.wall_left) - bool(depth.wall_right)
                inter.apply_rotation(depth_steering_direction * 0.5, 0)
            
            # level horizon to not get stuck looking up or down
            if loop_current_time > last_horizon_level_time + level_horizon_seconds:
                last_horizon_level_time = loop_current_time
                inter.level_horizon(in_game_sensitivity, in_game_speed)
            
            time.sleep(threading_loop_speed_limit_time)
        
        # safety precaution for threading
        time.sleep(threading_loop_speed_limit_time)

targeting.refresh_update = recieve_fresh_targeting_update
targeting.targeting_sensor_refreshing = True
depth.depth_sensor_refreshing = False

behaviour_thread = threading.Thread(target=main_behaviour)
behaviour_thread.start()