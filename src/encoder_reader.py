"""! @file encoder_reader.py


"""


import pyb

  
__AUTO_RELOAD_VALUE = 10000

class Encoder:

    """
        Specifies and sets up an encoder counter using the internal timers.
        Designed for quadrature encoders with two channels and no reset.
        Handles any issues with timer overflow to allow for ease of use.
    """

    def __init__ (self, 
                  inApin: pyb.Pin.board,
                  inBpin: pyb.Pin.board,
                  timer_num: int,
                  af_mode: int
                  ):
        """! 
            Creates an encoder timer that counts
            @param inApin Pyboard pin used to read encoder channel A
            @param inBpin Pyboard pin used to read encoder channel B
            @param timer_num Timer number associated with pin alternate functions
            @param af_mode Alternate function timer to use
        """

        self.__encA_pin = pyb.Pin(inApin, mode=pyb.Pin.AF_PP, af=af_mode)
        self.__encB_pin = pyb.Pin(inBpin, mode=pyb.Pin.AF_PP, af=af_mode)
        self.__enc_timer = pyb.Timer(timer_num, prescaler=0, period=__AUTO_RELOAD_VALUE-1)
        
        self.__timer_channel = self.__enc_timer.channel(1,pyb.Timer.ENC_AB)

        self.zero()
    

    def read(self):

        """! 
            Read the current position
            @return Position since last zero
        """        

        current_count = self.__enc_timer.counter()

        count_delta = self.__last_count - current_count

        if(abs(count_delta) > __AUTO_RELOAD_VALUE/2):

            if(count_delta < 0):
                count_delta += __AUTO_RELOAD_VALUE-1

            else:
                count_delta -= __AUTO_RELOAD_VALUE-1

        self.__last_count = current_count

        self.__position += count_delta

        return self.__position
    

    def zero(self):

        """! 
            Zeros out the position reading
        """

        self.__last_count = 0
        self.__position = 0
        self.__enc_timer.counter(0)
        

