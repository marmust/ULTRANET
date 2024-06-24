from ultra_interface import ultrakill_interface
from importlib import reload
import keyboard
import time

class main():

    # This class will be used to run everything, and all of the main logic is implemented here. You do not need to touch this or create subclasses of it, just initialize and call the run function

    def __init__(self, action_modules, sensor_modules, strategy, interface_data):
        self.interface = ultrakill_interface(*interface_data) # Setup the interface
        self.action_modules = {a.__name__:a(self.interface) for a in action_modules} # Initialize action modules with the interface, indexed by their name
        self.sensor_modules = {a.__name__:(a(), None) for a in sensor_modules} # Initialize all sensor modules in a dictionary indexed by their name. The tuple here is (sensor_module, sensor_data) Where sensor data is used to keep track of the output of the sensor
        self.strategy = strategy(self.action_modules.keys()) # Initialize the main strategy, giving it a list of the names of action modules
        self.required_sensors = self.strategy.required_sensors # This list will be used to keep track of which sensor modules the strategy needs, and thus which sensor modules should be run every time
        for sensor in self.required_sensors:
            if not sensor in self.sensor_modules.keys():
                raise NotImplementedError("Required Sensor Module Missing! " + sensor)
        self.fps = []

    def run(self):
        t1 = time.time()
        screenshot = self.interface.get_game_screenshot() # Get screenshot from the game to use
        strategy_in = [] # A list of sensor outputs to be input to the strategy
        for sensor in self.required_sensors: # Iterating over sensors needed for the strategy
            self.sensor_modules[sensor] = (self.sensor_modules[sensor][0], self.sensor_modules[sensor][0].run(screenshot)) # Set the sensor data (indexed at 1) to the output of the sensor module (indexed at 0)
            strategy_in.append(self.sensor_modules[sensor][1]) # Add the sensor data to the list of inputs to the strategy
        module = self.strategy.run(*strategy_in) # Run the strategy to determine which module should be run
        reqs = self.action_modules[module].required_sensors # Get the required sensors list from the action module chosen
        action_in = [] # Setup the list of sensor data to be input into the action module
        for sensor in reqs: # Iterate over required sensors for the action module
            if not sensor in self.sensor_modules.keys():
                raise NotImplementedError("Required Sensor Module Missing! " + sensor)
            elif not sensor in self.required_sensors: # The sensor data has not been calculated yet, so it needs to be
                self.sensor_modules[sensor] = (self.sensor_modules[sensor][0], self.sensor_modules[sensor][0].run(screenshot)) # This sensor hasn't been run for the strategy, so get the sensor data (indexed at 1) to the output of the sensor module (indexed at 0)
                action_in.append(self.sensor_modules[sensor][1]) # Append the result to the action module input list
            else: # This sensor has already been run for the strategy
                action_in.append(self.sensor_modules[sensor][1]) # Appends the already calculated sensor data to the action module input list
        self.action_modules[module].run(*action_in) # Run the action module with all of the inputs that it needs
        self.fps.append(1/(time.time()-t1))
        if len(self.fps) > 100:
            self.fps.__delitem__(0)
            print(f"Running at approx {sum(self.fps)/100} fps")

import config

while True:
    try:
        reload(config)
        from config import *
        runner = main(ACTION_MODULES, SENSOR_MODULES, STRATEGY, INTERFACE_DATA)
        while not (keyboard.is_pressed("End") or keyboard.is_pressed("Home")):
            runner.run()
        if keyboard.is_pressed("End"):
            break
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        runner.interface.cam.release()