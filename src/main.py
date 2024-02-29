"""! @file main.py

"""

import pyb
import utime
import micropython
import PID_controller
from motor_driver import MotorDriver as Motor
from servo_driver import ServoDriver as Servo
import encoder_reader
import platform
import cotask
import task_share
import gc

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue, task_share

#Allocate memory for debug dump
micropython.alloc_emergency_exception_buf(100)


## Constant defining the pin to be used for channel A of the encoder
ENCODER1_PIN_A = pyb.Pin.board.PB6
## Constant defining the pin to be used for channel B of the encoder
ENCODER1_PIN_B = pyb.Pin.board.PB7
## Enable pin for the motor driver
MOTOR1_EN_PIN = pyb.Pin.board.PC1
## Motor 1 channel B control pin
MOTOR1_INB_PIN = pyb.Pin.board.PA1
## Motor 1 channel A control pin
MOTOR1_INA_PIN = pyb.Pin.board.PA0

MOTOR1_SPEED_TASK_PRIORITY = 2
MOTOR1_SPEED_TASK_PERIOD = 10

MOTOR1_POSITION_TASK_PRIORITY = 3
MOTOR1_POSITION_TASK_PERIOD = 10

MOTOR1_CONTROLLER_TASK_PRIORITY = 1
MOTOR1_CONTROLLER_TASK_PERIOD = 10

MOTOR1_PRINTING_TASK_PRIORITY = 4
MOTOR1_PRINTING_TASK_PERIOD = 10

HB_TASK_PRIORITY = 99
HB_TASK_PERIOD = 1000

# servo task setup
SERVO1_POS_UPDATE_PRIO = 10
SERVO1_POS_UPDATE_PERIOD = 10   # arbitrary, unsure of correct value

# constants to set servo freq to 50hz w/ tick int of 1us
SERVO_ARR = 19999
SERVO_PS = 79

# servo angle specific constants
SERVO1_MIN_PULSE = 600      # uSec
SERVO1_MAX_PULSE = 2600     # uSec
SERVO1_ANGLE_RANGE = 180    # deg

# servo pin and timer declarations
SERVO1_PIN = pyb.Pin.board.PA8
SERVO1_TIMER_NUM = 1
SERVO1_TIMER_CHAN = 1

## Constant defining the timer number of the pins used for encoder 1
ENCODER1_TIMER_NUMBER = 4 

## Maximum time to wait before ending the step response test in ms
TIMEOUT_MS = 2000


def heartbeat(shares):

    task_state_share = shares

    while True:

        state = task_state_share.get()

        if state == 0:
            pass

        else:
            print("beat")

        yield 0


def motor_printing(shares):

    position_share, controller_value_share, task_state_share = shares

    while True:

        state = task_state_share.get()

        if state == 0:
            start_time = utime.ticks_ms()
            pass

        else:
            print(str(utime.ticks_ms()-start_time) + "," + str(position_share.get()))

        yield 0



if __name__ == "__main__":

    '''SERVO 1 SETUP'''
    ## Servo 1 Object
    servo1 = Servo(SERVO1_PIN,
                   SERVO1_TIMER_NUM,
                   SERVO1_TIMER_CHAN,
                   SERVO1_MIN_PULSE,
                   SERVO1_MAX_PULSE,
                   SERVO1_ANGLE_RANGE,
                   SERVO_ARR,
                   SERVO_PS)

    ## Initialize servo 1 to nominal position (halfway thru range)
    # servo1.set_angle(SERVO1_ANGLE_RANGE/2)
    servo1.test_sweep_reset()


    '''MOTOR 1 SETUP'''
    ## Motor 1 Object
    motor1 = Motor(MOTOR1_EN_PIN, 
                  MOTOR1_INA_PIN, 2, 1,
                  MOTOR1_INB_PIN, 2, 2,
                  30000)
    
    #Initialize motor to safe state
    motor1.set_enable(1)
    motor1.set_duty_cycle(0)


    '''MOTOR 1 ENCODER SETUP'''
    ## Motor 1 encoder object
    encoder1 = encoder_reader.Encoder(ENCODER1_PIN_A, ENCODER1_PIN_B, ENCODER1_TIMER_NUMBER, pyb.Pin.AF2_TIM4)


    '''MOTOR 1 PID CONTROL SETUP'''
    ## Current position of motor 1 in encoder ticks
    position1 = 0

    ## Target motor position in encoder ticks
    step_target = 16384

    ## PID controller object for motor 1
    controller1 = PID_controller.PIDController(Kp=0.03, init_target=step_target, Ki = 0.0001)



    ## Flag defining the end of the step response routine
    done = False



    '''MOTOR 1 TASKS SETUP'''
    # Create a share and a queue to test function and diagnostic printouts
    motor1_position = task_share.Share('l', thread_protect=False, name="Motor 1 Share") #initialized with signed long
    motor1_controller_value = task_share.Share('f', thread_protect=False, name="Motor 1 Control Val") #initialized with float
    motor1_task_state = task_share.Share('l', thread_protect=False, name="Motor 1 Task State") #initialized with signed long


    motor1_speed_task = cotask.Task(motor1.set_duty_cycle_task, name="motor1_speed_task", priority=MOTOR1_SPEED_TASK_PRIORITY, 
                            period=MOTOR1_SPEED_TASK_PERIOD,
                            profile=True, trace=True, shares=(motor1_controller_value, motor1_task_state))
    

    motor1_position_task = cotask.Task(encoder1.read_task, name="motor1_position_task", priority=MOTOR1_POSITION_TASK_PRIORITY, 
                            period=MOTOR1_POSITION_TASK_PERIOD,
                            profile=True, trace=True, shares=(motor1_position, motor1_task_state))
    

    motor1_controller_task = cotask.Task(controller1.run_task, name="motor1_controller_task", priority=MOTOR1_CONTROLLER_TASK_PRIORITY, 
                            period=MOTOR1_CONTROLLER_TASK_PERIOD,
                            profile=True, trace=True, shares=(motor1_position, motor1_controller_value, motor1_task_state))
    
    motor1_print_task = cotask.Task(motor_printing, name="motor1_print_task", priority=MOTOR1_CONTROLLER_TASK_PRIORITY, 
                            period=MOTOR1_CONTROLLER_TASK_PERIOD,
                            profile=True, trace=True, shares=(motor1_position, motor1_controller_value, motor1_task_state))


    '''SERVO 1 TASKS SETUP'''
    servo1_sweep_task = cotask.Task(servo1.test_sweep_run, name="servo1_position_task", priority=SERVO1_POS_UPDATE_PRIO, 
                            period=SERVO1_POS_UPDATE_PERIOD,
                            profile=True, trace=True, shares=(motor1_task_state))

    '''OTHER TASKS'''
    heartbeat_task = cotask.Task(heartbeat, name="heartbeat_task", priority=HB_TASK_PRIORITY, 
                            period=HB_TASK_PERIOD,
                            profile=True, trace=True, shares=(motor1_task_state))
    

    motor1_task_state.put(0)
    
    cotask.task_list.append(motor1_speed_task)
    cotask.task_list.append(motor1_position_task)
    cotask.task_list.append(motor1_controller_task)
    cotask.task_list.append(heartbeat_task)
    cotask.task_list.append(motor1_print_task)
    cotask.task_list.append(servo1_sweep_task)


    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()



    start_time = 0
    

    '''MAIN LOOP'''
    try:

        while 1:

            cotask.task_list.pri_sched()

            # for idx,value in enumerate(time_values):
            #     print(str(value) + "," + str(position_values[idx]))
            
            if (utime.ticks_ms()-start_time) > TIMEOUT_MS:
                motor1_task_state.put(0)
                motor1.set_duty_cycle(0)
                #print("Done")

                
            if pyb.USB_VCP().any():

                ## Raw value read by the serial bus
                serial_value = pyb.USB_VCP().read()

                ## Requested Kp value, converted from serial data
                received_Kp = float(serial_value.decode().strip('\n'))

                controller1.set_Kp(received_Kp)

                ## Time at which the step response test was started in ms
                start_time = utime.ticks_ms()

                done = False

                encoder1.zero()

                ## Time since the start of the step response routine in ms
                current_time_ms_appx = 0

                ## List containing recorded position values 
                position_values = []
                ## List containing recorded time values 
                time_values = []

                ## Time of previous iteration and used to execute the PID at a known period
                last_time = start_time

                motor1_task_state.put(1)

        
    except KeyboardInterrupt:
        pass

    motor1.set_duty_cycle(0)
    servo1.reset_pulse_width()

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(motor1_speed_task.get_trace())
    print(motor1_position_task.get_trace())
    print(motor1_controller_task.get_trace())
    print('')