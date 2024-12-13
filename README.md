
# ULTRANET
A framework for a fully modular ULTRAKILL playing agent

(A rewrite of [this](https://youtu.be/16zgLzC1eDE))

Original concept/code/idea/literally everything by [8AAFFF](https://www.youtube.com/@8AAFFF)

Code (mostly) rewritten by [CTAG](https://www.youtube.com/@ctag07)


### ⚠ WARNING:
This bot currently uses raw mouse movement for turning, so it can cause a lot of flashing and stuttering within it's movement.
This is because mouse and keyboard input are a lot easier to control precisely 

----

### HOW TO RUN:

Change anything you want in the config.py file, they work are as follows:
<dl>
    <dt> SENSOR_MODULES: </dt>
    <dd>
        A list of the sensor modules to include for the bot<br>
        Sensor modules are things that take in a screenshot of the game and output data for other modules to use<br>
        This has to include every required sensor module for the strategy and all action modules
    </dd>
    <dt> ACTION_MODULES </dt>
    <dd>
        A list of the action modules to include for the bot<br>
        Action modules take in data from sensor modules and use the interface to control V1<br>
        You shouldn't have to include any specific action modules because strategies shouldn't be reliant on specific modules<br>
        Add and remove modules as you please, but if the strategy you use doesn't have a module implemented it won't be used
    </dd>
    <dt>STRATEGY:</dt>
    <dd>
        The strategy module that you want to use<br>
        Strategy modules take in data from sensor modules and decide which action module should be run each iteration<br>
        This can be any strategy module you want
    </dd>
    <dt>INTERFACE_DATA:</dt>
    <dd>
        A list of numbers important for the bot to be able to properly play, make sure to fill all these out with your own values beforehand!<br>
        The bot uses some of these for things like deciding how much to turn, or how fast things should be run
    </dd>
</dl>

Then, run main.py and let it start up! (Make sure to alt tab into ultrakill before it's done starting up, otherwise it will take control of your keyboard early!)
If you want to reload the bot at any time, press the home key
If you want to stop the bot at any time, press the end key

----

### MAKING MODULES:

This framework is designed to be hyper-modular, with literally everything contained within a module that's plug-and-play at all times.
<dl>
    <dt>SENSOR MODULES:</dt>
    <dd>
        <ol>
        <li>Look at the base_sensor_module.py for an example of how a sensor module should be structured</li>
        <li>Create a new python file in the sensor modules folder, and create a class there that inherits from the base sensor module class</li>
        <li>Then implement the init and run methods for the sensor, making sure it outputs appropriate data for whatever kind of sensor it is</li>
        </ol>
    </dd>
    <dt>ACTION MODULES:</dt>
    <dd>
        <ol>
            <li>Look at the base_action_module.py for an example of how an action module should be structured </li>
            <li>Create a new python file in the action modules folder, and create a class there that inherits from the base action module class</li>
            <li>Then implement the init and run methods for the action module, with the init function calling the init method for it's parent class with the interface to set the interface variable</li>
            <li>Also make sure to update the required_sensors list with the list of sensors that the action module needs to run</li>
            <li>The data from these sensors will be input into the run function of your action module in the order that you list them in, so keep that in mind</li>
            <li>You can use the interface to do practically anything you need with v1</li>
        </ol>
    </dd>
    <dt>STRATEGY MODULES:</dt>
    <dd>
        <ol>
            <li>Look at the base_strategy.py for an example of how a strategy module should be structured</li>
            <li>Create a new python file in the strategies folder, and create a class there that inherits from the base strategy module class</li>
            <li>Then implement the init and run methods for the strategy module, with the init function calling the init method for it's parent class with the list of action module name and value pairs</li>
            <li>Also make sure to update the required sensors list with the list of sensors that the strategy needs to run</li>
            <li>The data from these sensors will be input into the run function of your strategy in the order that you list them in, so keep that in mind</li>
            <li>Best practice is to make if statements to apply values for each module, so that if a module isn't present from the user it won't error, and it will make do with the enabled modules</li>
        </ol>
    </dd>
</dl>

----

I'm pretty sure the dude who originally made this should accept pr's and they're definitely appreciated<br>
Can't wait to see how far this goes! :D
