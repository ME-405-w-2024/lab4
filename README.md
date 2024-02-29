# Lab 4 for ME405 at California Polytechnic University

## Contributors: Kevin Jung, Aidan Schwing, Noah Fitzgerald

Mircopython for deployment on NUCLEO-L476RG

Documentation available at: https://me-405-w-2024.github.io/lab4/

The code present in this repository implements a task-sharing regime to control multiple actuators simultaneously. 

`display.py` is intended to run on a separate computer from the STM32 based microcontroller, and sends run commands to the microcontroller over serial data channels.

`main.py` implements the task-sharing functionality. Tasks are implemented through use of `cotask.py`, available [here](https://github.com/spluttflob/ME405-Support). Objects are instantiated with previously developed drivers. Motor control is split into multiple tasks which read, set, and calculate relevant control signals. Servo control is handled simultaneously with a separate task for setting position via PWM signal. 

When a controller task is run too slowly, the system fails to adequately control the actuator. This is seen in the plot below. A recommended minimum speed for adequate motor control is ***100 Hz***. 

Example response running controller below 100 Hz:
![100ms controller period](https://github.com/ME-405-w-2024/lab4/blob/main/ControllerSpeedResponses/100ms.png)

Example response running controller above 100 Hz:
![10 ms controller period](https://github.com/ME-405-w-2024/lab4/blob/main/ControllerSpeedResponses/10ms.png)
