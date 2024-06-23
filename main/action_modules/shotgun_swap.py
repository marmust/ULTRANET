from .base_action_module import action_module
import torch as pyt
import time
import keyboard

IMPORTANCE_WEIGHTS = pyt.tensor((1.0, 1.0,  # x and y
                                0.2, 0.2,  # width and height
                                0.0, 1.0), # confidence and class
                                dtype=pyt.float32)
WHIPLASH_THRESHOLD = 0.001 # Threshold at which it tries to whiplash the target
BACKUP_THRESHOLD = 0.05 # Threshold at which it tries to backup from the target
WANTED_THRESHOLD = 0.03
MOUSE_MAGIC = 3 # Random number that I felt out that assists in aiming properly without jumping all over the place, although it still does that

class shotgun_swap(action_module):

    required_sensors = ["yolo_sensor"]

    def __init__(self, interface):
        super().__init__(interface)
        self.interface = interface
        self.target_detected = False
        self.target = None
        self.target_class = 0
        self.last_swapped = time.time()

    def run(self, yolo_sensor_data):

        current_time = time.time()

        if len(yolo_sensor_data) > 0: # Targets found

            # If we don't have the shotgun out, then pull it out
            if self.interface.current_weapon != 1:
                self.interface.switch_weapon_to(1)

            if not self.target is None: # We have a target
                self.target = self.find_recurring_target(yolo_sensor_data) # Try to keep tracking previous target
            else: # No target yet
                # Choose the closest target to the crosshair
                xy_positions = yolo_sensor_data[:, :2]
                target_idx = pyt.argmin(pyt.sum(pyt.pow(xy_positions, 2), dim=1))
                self.target = yolo_sensor_data[target_idx]
    
            target_size = pyt.prod(self.target[2:4]) # Get bounding box size of target
            self.interface.apply_movement((target_size.item() < WANTED_THRESHOLD)*2-1, (int(current_time*3)%2)*2-1) # Some messy math, but basically switch strafing direction every third of a second
            
            if target_size < WHIPLASH_THRESHOLD: # Target is too far away
                self.interface.whiplash() # Whiplash target
            elif target_size > BACKUP_THRESHOLD: # Target is too close
                self.interface.dash() # Dash away from target
            
            if current_time - self.last_swapped > 0.45: # Been at least 0.45 seconds from the last shotgun swap we did, so shoot and swap
                self.interface.main_fire_tap(0.01)
                self.interface.switch_variation_up()
                self.last_swapped = time.time()
            
            x, y = self.target[0].item() * self.interface.aspect_ratio[0] - (0.5 * self.interface.aspect_ratio[0]), self.target[1].item() * self.interface.aspect_ratio[1] - (0.5 * self.interface.aspect_ratio[1]) # Get the X and Y values of the bounding box, then normalize them with the screem size
            x = x * 63356 / self.interface.aspect_ratio[0] / self.interface.sensitivity / MOUSE_MAGIC
            y = y * 63356 / self.interface.aspect_ratio[1] / self.interface.sensitivity / MOUSE_MAGIC
            self.interface.apply_rotation(x, y)
    
        else:

            # No enemy spotted, so reset the target to None
            self.target = None
            self.interface.apply_movement(0, 0) # Stop in our tracks for more efficient rotation
            self.interface.apply_rotation(20, int(current_time)%2*20-10) # No target on screen, turn to the right, swapping every second between looking up and down
            self.interface.jump() # Jump up in the air so walls can't keep us from seeing enemies

    def find_recurring_target(self, current_tensor):
        # Repeat the importance weights tensor and send it to the correct device
        importance_weights = IMPORTANCE_WEIGHTS.repeat((current_tensor.size()[0], 1)).to(current_tensor.device)
        
        # Repeat the target box
        repeated_target = self.target.repeat((current_tensor.size()[0], 1))
        
        # Calculate the differences between the each of the current tensors and the target, and multiply by the importance weights
        difference_tensor = pyt.abs(current_tensor - repeated_target) * importance_weights
        
        # Sum the differences for each of the bounding boxes and find the closest one to the target
        found_tracked_object = current_tensor[pyt.argmin(pyt.sum(difference_tensor, dim=1))]
        
        return found_tracked_object