from .base_strategy import strategy_module
import time

ATTACK_GIVEUP_TIME = 8

class basic_strategy(strategy_module):
    
    required_sensors = ["yolo_sensor"]

    def __init__(self, action_modules):
        super().__init__(action_modules)
        self.last_enemy_spotted = time.time()

    def run(self, yolo_data):
        current_time = time.time()
        
        if len(yolo_data) > 0: # There are enemies spotted
            self.last_enemy_spotted = current_time # Update the time the last enemy was spotted at
        
        if "shotgun_swap" in self.action_modules.keys(): # Check if shotgun_swap module is active
            # The shotgun swap module has a priority of 1 if there are enemies on screen or not enough time has passed since the last enemy was spotted
            self.action_modules["shotgun_swap"] = 1 if len(yolo_data) > 0 or current_time-self.last_enemy_spotted < ATTACK_GIVEUP_TIME else 0
        
        if "basic_nav" in self.action_modules.keys(): # Check if basic_nav module is active
            # The basic nav module has a priority of 1 if there are no enemies on screen and enough time has passed since the last enemy was spottes
            self.action_modules["basic_nav"] =  1 if len(yolo_data) == 0 and current_time-self.last_enemy_spotted >= ATTACK_GIVEUP_TIME else 0
        
        # Return the action module with the highest priority, this code is a little messy but I couldn't find an easier way to do it
        return list(self.action_modules.keys())[list(self.action_modules.values()).index(max(self.action_modules.values()))]