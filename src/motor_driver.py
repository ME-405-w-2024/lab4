"""! @file motor_driver.py

Contains a class to drive brushed DC motors using the IHM04A1 motor driver from ST.
https://www.st.com/en/ecosystems/x-nucleo-ihm04a1.html
Supports bi-directional operation and speed control through PWM.
"""

import pyb


class MotorDriver:
    """! 
    This class implements a motor channel on the IHM04A1
    """




    def __init__ (self, 
                  en_pin: pyb.Pin.board, 
                  in1pin: pyb.Pin.board, in1_timer_num: int, in1_timer_channel_number: int, 
                  in2pin: pyb.Pin.board, in2_timer_num: int, in2_timer_channel_number: int, 
                  pwm_frequency: int):
        """! 
            Creates a motor driver by initializing GPIO pins and turning off the motor for safety. 
            @param en_pin Pyboard pin used to enable the respective channel on the IHM04A1
            @param in1pin Pyboard pin controlling channel 1 of the H-bridge
            @param in1_timer_num Timer number associated with the Pyboard pin defined in in1pin
            @param in1_timer_channel_number Timer channel associated with the Pyboard pin defined in in1pin
            @param in2pin Pyboard pin controlling channel 2 of the H-bridge
            @param in2_timer_num Timer number associated with the Pyboard pin defined in in2pin
            @param in2_timer_channel_number Timer channel associated with the Pyboard pin defined in in2pin
            @param pwm_frequency Frequency to initialize the PWM for this driver channel
        """

        self.__en_pin = pyb.Pin(en_pin, pyb.Pin.OUT_PP)

        self.__pin1_timer_channel = self.__setupmotor__(in1pin, in1_timer_num, in1_timer_channel_number, pwm_frequency)
        self.__pin2_timer_channel = self.__setupmotor__(in2pin, in2_timer_num, in2_timer_channel_number, pwm_frequency)

        
    def __setupmotor__(self, inpin: pyb.Pin.board, in_timer_num: int, in_timer_channel_number: int, pwm_frequency: int):
        """! 
            Creates the proper PWM setup for each motor pin
            @param inpin Pyboard pin controlling the channel of the H-bridge
            @param in_timer_num Timer channel associated with the H-bridge control pin on the Pyboard
            @param in_timer_channel_number Timer channel number associated with the H-bridge control pin on the Pyboard
            @param pwm_frequency Frequency to initialize the PWM for this H-bridge
        """
        pwm_pin = pyb.Pin(inpin, pyb.Pin.OUT_PP)
        pwm_timer = pyb.Timer (in_timer_num , freq=pwm_frequency)
        timer_channel = pwm_timer.channel(in_timer_channel_number, pyb.Timer.PWM, pin=pwm_pin)
        return timer_channel


    def set_enable(self, value: int):
        """! 
        Enables the motor driver channel
        @param value Value of the enable pin. 1 is enabled, 0 is disabled
        """
        self.__en_pin.value(value)


    def set_duty_cycle (self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor 
        """
        #print (f"Setting duty cycle to {level}")


        if(level < 0):
            self.__pin1_timer_channel.pulse_width_percent(level * -1)
            self.__pin2_timer_channel.pulse_width_percent(0)
        else:
            self.__pin1_timer_channel.pulse_width_percent(0)
            self.__pin2_timer_channel.pulse_width_percent(level)

    