from ultra_interface import Ultrakill_Interface

class sensor_module():

    def __init__(self):
        # If you need to init anything here, do that now
        pass

    def run(self, image):
        # Take in an image, and output whatever data you want that goes out about it
        return image

class action_module():

    # Overwrite this with the sensors that are needed to be input into the run function, in order
    required_sensors = ["sensor"]

    def __init__(self, interface):
        # If you need to init anything here, do that now
        self.interface = interface

    def run(self, sensor_data):
        # Replace the inputs with the sensor data variables, in order. Then do whatever with it idk
        pass

class strategy_module():
    
    # Overwrite this with the sensors that the strategy needs to determine which action module to run, in order
    required_sensors = ["sensor"]

    def __init__(self, action_modules):
        # If you need to init anything here, do that now
        self.action_modules = {a: 0 for a in action_modules} # Keep this line here, action modules should be input as the names instead of the actual action modules
    
    def run(self, sensor_data):
        # Implement logic here to choose a module from the sensor data. MAKE SURE to not be dependant on certain modules to run, and decide on which module to run based on the list it is given
        return self.action_modules.keys()[0] # This just returns the first module, sooooooo

class main():

    # This class will be used to run everything, and all of the main logic is implemented here. You do not need to touch this or create subclasses of it, just initialize and call the run function

    def __init__(self, action_modules, sensor_modules, strategy, interface_data):
        self.interface = Ultrakill_Interface(*interface_data) # Setup the interface
        self.action_modules = {type(a).__name__:a(self.interface) for a in action_modules} # Initialize action modules with the interface, indexed by their name
        self.sensor_modules = {type(a).__name__:(a(), None) for a in sensor_modules} # Initialize all sensor modules in a dictionary indexed by their name. The tuple here is (sensor_module, sensor_data) Where sensor data is used to keep track of the output of the sensor
        self.strategy = strategy(action_modules) # Initialize the main strategy, giving it a list of action modules
        self.required_sensors = self.strategy.required_sensors # This list will be used to keep track of which sensor modules the strategy needs, and thus which sensor modules should be run every time
            
    def run(self):
        while True:
            screenshot = self.interface.get_game_screenshot() # Get screenshot from the game to use
            strategy_in = [] # A list of sensor outputs to be input to the strategy
            for sensor in self.required_sensors: # Iterating over sensors needed for the strategy
                self.sensor_modules[sensor][1] = self.sensor_modules[sensor][0].run(screenshot) # Set the sensor data (indexed at 1) to the output of the sensor module (indexed at 0)
                strategy_in.append(self.sensor_modules[sensor][1]) # Add the sensor data to the list of inputs to the strategy
            module = self.strategy.run(*strategy_in) # Run the strategy to determine which module should be run
            reqs = self.action_modules[module].required_sensors # Get the required sensors list from the action module chosen
            action_in = [] # Setup the list of sensor data to be input into the action module
            for sensor in reqs: # Iterate over required sensors for the action module
                if not sensor in self.required_sensors: # The sensor data has not been calculated yet, so it needs to be
                    self.sensor_modules[sensor][1] = self.sensor_modules[sensor][0].run(screenshot) # This sensor hasn't been run for the strategy, so get the sensor data (indexed at 1) to the output of the sensor module (indexed at 0)
                    action_in.append(self.sensor_modules[sensor][1]) # Append the result to the action module input list
                else: # This sensor has already been run for the strategy
                    action_in.append(self.sensor_modules[sensor][1]) # Appends the already calculated sensor data to the action module input list
            self.action_modules[module].run(*action_in) # Run the action module with all of the inputs that it needs