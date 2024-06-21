class action_module():

    # Overwrite this with the sensors that are needed to be input into the run function, in order
    required_sensors = ["sensor"]

    def __init__(self, interface):
        # If you need to init anything here, do that now
        self.interface = interface

    def run(self, sensor_data):
        # Replace the inputs with the sensor data variables, in order. Then do whatever with it idk
        pass