"""! @file main.py

"""

import pyb
import utime
import micropython
import PID_controller
from motor_driver import MotorDriver as Motor
import encoder_reader
import platform

if "MicroPython" not in platform.platform():
    from me405_support import cotask, cqueue

#Allocate memory for debug dump
micropython.alloc_emergency_exception_buf(100)

## Constant that sets the main task execution period
TASK_DELAY_MS = 10

## Constant defining the pin to be used for channel A of the encoder
ENCODER1_PIN_A = pyb.Pin.board.PB6

## Constant defining the pin to be used for channel B of the encoder
ENCODER1_PIN_B = pyb.Pin.board.PB7

## Constant defining the timer number of the pins used for encoder 1
ENCODER1_TIMER_NUMBER = 4 

## Maximum time to wait before ending the step response test in ms
TIMEOUT_MS = 2000


if __name__ == "__main__":
    
    ## Motor 1 encoder object
    encoder1 = encoder_reader.Encoder(ENCODER1_PIN_A, ENCODER1_PIN_B, ENCODER1_TIMER_NUMBER, pyb.Pin.AF2_TIM4)


    ## Enable pin for the motor driver
    en_pin = pyb.Pin.board.PC1
    ## Motor 1 channel B control pin
    in1b_pin = pyb.Pin.board.PA1
    ## Motor 1 channel A control pin
    in1a_pin = pyb.Pin.board.PA0


    ## @var motor
    # Motor 1 driver

    motor = Motor(en_pin, 
                  in1a_pin, 2, 1,
                  in1b_pin, 2, 2,
                  30000)
    
    motor.set_enable(1)
    motor.set_duty_cycle(0)


    ## Current position of motor 1 in encoder ticks
    position1 = 0

    ## Target motor position in encoder ticks
    step_target = 16384

    ## PID controller object for motor 1
    p_controller1 = PID_controller.PIDController(Kp=0.005, init_target=step_target, Ki = 0.0001)


    ## Flag defining the end of the step response routine
    done = False



    try:

        while 1:

            if pyb.USB_VCP().any():

                ## Raw value read by the serial bus
                serial_value = pyb.USB_VCP().read()

                ## Requested Kp value, converted from serial data
                recieved_Kp = float(serial_value.decode().strip('\n'))

                p_controller1.set_Kp(recieved_Kp)

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

                while not done:

                    if (utime.ticks_ms() - last_time) >= TASK_DELAY_MS :

                        current_time_ms_appx += (utime.ticks_ms() - last_time)

                        last_time = utime.ticks_ms()

                        position1 = encoder1.read()

                        ## Current motor controller request value from the PID controller
                        control1_value = p_controller1.run(position1)

                        motor.set_duty_cycle(int(control1_value))
                        
                        position_values.append(position1)

                        time_values.append(current_time_ms_appx)


                    if (utime.ticks_ms()-start_time) > TIMEOUT_MS:
                        done = True
                        print("Done")


                for idx,value in enumerate(time_values):
                    print(str(value) + "," + str(position_values[idx]))

                
                
    
            motor.set_duty_cycle(0)
            utime.sleep_ms(TASK_DELAY_MS)

        
    except KeyboardInterrupt:
        motor.set_duty_cycle(0)