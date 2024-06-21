class strategy_module():
    
    # Overwrite this with the sensors that the strategy needs to determine which action module to run, in order
    required_sensors = ["sensor"]

    def __init__(self, action_modules):
        # If you need to init anything here, do that now
        self.action_modules = {a: 0 for a in action_modules} # Keep this line here, action modules should be input as the names instead of the actual action modules
    
    def run(self, sensor_data):
        # Implement logic here to choose a module from the sensor data. MAKE SURE to not be dependant on certain modules to run, and decide on which module to run based on the list it is given
        return self.action_modules.keys()[0] # This just returns the first module, sooooooo