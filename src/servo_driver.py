"""! @file servo_driver.py

Contains a class to drive basic servo motors. 
Supports servo angle control via PWM pulse width.
Initialization supports setting of upper and lower bounds for the pulse width determining servo angle.
Further information about basic servo theory is available here:
https://deepbluembedded.com/stm32-servo-motor-control-with-pwm-servo-library-examples-code/
"""

import pyb

class ServoDriver:
    """!
    This class implements a servo controlled with PWM pulse width
    """

    def __init__(self,
                 pwm_pin: pyb.Pin.board, pwm_timer_num: int, pwm_channel_num: int,
                 pwm_min_pulse: int, pwm_max_pulse: int, full_angle_range: int,
                 period_ARR: int, period_PS: int 
                 ):
        """! 
            Creates a servo driver by initializing GPIO pins.
            @param pwm_pin Pyboard pin controlling channel 1 of the H-bridge
            @param pwm_timer_num Timer number associated with the Pyboard pin defined in in1pin
            @param pwm_channel_num Timer channel associated with the Pyboard pin defined in in1pin
            @param pwm_min_pulse Minimum pulse width given in ms, used to calculate angle range
            @param pwm_max_pulse Maximum pulse width given in ms, used to calculate angle range
            @param full_angle_range Difference in physical angle for given min and max pulse
            @param period_ARR Auto reload value to use for timer
            @param period_PS Pre-scale value to use for timer
        """        

        # set self values for the pulse information
        self.__pwm_min_pulse = pwm_min_pulse
        self.__pwm_max_pulse = pwm_max_pulse
        self.__full_angle_range = full_angle_range

        # set up a pin to write pwm to 
        self.__pwm_pin = pyb.Pin(pwm_pin, pyb.Pin.OUT_PP)
        # set up the timer using the set auto reload and pre-scaler
        self.__pwm_timer = pyb.Timer(pwm_timer_num, period=period_ARR, prescaler=period_PS)
        # assign the channel to the given pin
        self.__pwm_timer_chan = self.__pwm_timer.channel(pwm_channel_num, pyb.Timer.PWM, pin=self.__pwm_pin)
        
        # determine the applicable angle resolution that can be used
        self.__angle_res = (pwm_max_pulse - pwm_min_pulse) / full_angle_range   # resolution in counts / deg

        self.sweep_angle = 0
 

    def set_angle(self,
                  angle: float):
        """!
            Sets the angle of the servo by converting a given angle in degrees to a valid count in pulse width.
            @param angle Takes a float angle value between 0 and the maximum given during instantiation. 
        """


        # add in functionality to prevent excess angle writes
        assert angle <= self.__full_angle_range, "Angle cannot be larger than given maximum"
        assert angle >= 0, "Angle cannot be non-positive"
        
        self.__angle = angle
    
        # convert the input angle to a count that can be passed into pulse_width
        angle_count = int( (self.__angle * self.__angle_res) + self.__pwm_min_pulse )

        #print(angle_count)
        self.__pwm_timer_chan.pulse_width(angle_count)


    def get_angle(self):
        """!
            Returns the current angle of the servo.
        """
        return self.__angle
    

    def reset_pulse_width(self):
        """!
            Resets the pulse width to zero to prevent running of the servo after program shutdown.
        """
        self.__pwm_timer_chan.pulse_width(0)



    def test_sweep_reset(self):
        """!
            Resets the current sweep angle.
        """
        self.sweep_angle = 0


    def test_sweep_run(self, shares):
        """!
            Ramps through the full range of valid integer angles every time this function is called. Intended to be used as a task.
            @param shares Includes the current task state to allow disabling of the servo
        """
        task_state_share = shares

        while 1:
            state = task_state_share.get()

            if state == 0:
                self.reset_pulse_width()
                pass
            else:
                if self.sweep_angle < self.__full_angle_range:
                    self.sweep_angle += 1
                    self.set_angle(self.sweep_angle)
                    print (self.sweep_angle)
                else:
                    self.sweep_angle = 0

            yield