import torch
import threading
import ultra_interface as inter
import time

net = torch.hub.load("ultralytics/yolov5", "custom", path=fr"../run_ai_only/model_weights/6_class_original_yolov5m.pt")

# info that this file returns
# !ACTIVE!
net_result = None
all_target_positions_list = []
all_target_sizes_list = [0]
are_targets_detected = False
is_target_locked = False
locked_target_class = 0
chosen_target_norm_position = [0, 0]
chosen_target_class = 0
# !PASSIVE!
class_to_string = net.names

# settings of this file
refresh_update = None
lock_inaccuracy_threshold = 2 # 1 = crosshair exactly inside target   |   > 1 = crosshair "close" to target   |   < 1 = crosshair inside box smaller than target
targeting_sensor_refreshing = False
agression = 1
anti_stick_drift_amount = 0.3
confidence_threshold = 0.5
threading_loop_speed_limit_time = 0.001

def run_image(image):
    # pass a screenshot thru the object detection net
    net_result = net(image)
    
    # filter if targets met confidence requirements
    accepted_net_results = net_result.xywhn[0][:, -2] > confidence_threshold
    filtered_net_result = net_result.xywhn[0][accepted_net_results]
    
    return net_result, filtered_net_result

def find_recurring_target_bnd_box(previous_bnd_box_tensor, current_raw_tensor, importance_weights_tensor="default"):
    if importance_weights_tensor == "default":
        importance_weights_tensor = torch.tensor((1.0, 1.0,  # x and y
                                                  0.2, 0.2,  # width and height
                                                  0.0, 0.0), # confidence and class
                                                 dtype=torch.float32,
                                                 device=current_raw_tensor.device).repeat((current_raw_tensor.shape[0], 1))
    
    # repeat the bnd_box_tenosr of the desired object to be the same shape as current_raw_tensor
    repeated_bnd_box = previous_bnd_box_tensor.repeat((current_raw_tensor.shape[0], 1))
    
    # calculate how different each candidate bnd box is from the target bnd box (apply weights too)
    difference_tensor = torch.abs(current_raw_tensor - repeated_bnd_box) * importance_weights_tensor
    
    # sum all difference parameters into a single digit
    absolute_difference = torch.sum(difference_tensor, dim=1)
    
    # the bnd box of the current_raw_tensor with the most similarity to the given target to track
    found_tracked_object = current_raw_tensor[torch.argmin(absolute_difference)]
    
    return found_tracked_object

def rotation_loop():
    global net_result
    global all_target_positions_list
    global all_target_sizes_list
    global chosen_target_norm_position
    global are_targets_detected
    global is_target_locked
    
    # initiate variables to default values
    targets_detected_flag = False
    
    while True:
        if targeting_sensor_refreshing:
            # pass a screenshot thru the net to get detections
            net_result, filtered_net_result = run_image(inter.get_game_screenshot())
             
            # check if any detections were even made
            are_targets_detected = len(filtered_net_result) > 0

            if are_targets_detected:
                if are_targets_detected != targets_detected_flag:
                    targets_detected_flag = are_targets_detected
                    
                # pick the closest to crosshair enemy to target (euclidian distance)
                enemy_xy_positions = filtered_net_result[:, :2] * 2 - 1
                chosen_target_idx = torch.argmin(torch.sum(torch.pow(enemy_xy_positions, 2), dim=1))
                chosen_target_bnd_box = filtered_net_result[chosen_target_idx]
                
                # a list of all target positions (sorted by class priority)
                all_target_positions_list = (filtered_net_result[:, 0:2] * 2 - 1)[torch.argsort(filtered_net_result[:, -1])].tolist()
                all_target_sizes_list = torch.prod(filtered_net_result[:, 2:4], dim=1)[torch.argsort(filtered_net_result[:, -1])].tolist()
                # the normalized position of the currently chosen to be tracked enemy
                chosen_target_norm_position = (chosen_target_bnd_box[:2] * 2 - 1).tolist()
                
                # tell main that fresh data is available
                if refresh_update != None:
                    refresh_update()
            else:
                targets_detected_flag = are_targets_detected
        else:
            time.sleep(threading_loop_speed_limit_time)
            
# put head rotation loop on different thread
head_rotation_thread = threading.Thread(target=rotation_loop)
head_rotation_thread.start()
print(f"{__name__}   --->   started targeting_sensor thread succesfully (stop from task manager)")