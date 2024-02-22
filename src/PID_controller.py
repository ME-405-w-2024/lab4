"""! @file PID_controller.py


"""

class PIDController:
    """
    Class representing a PID controller with feed-forward compensation
    Contains provisions for setting all gain and setpoint values on the fly
    """

    def __init__(self, Kp, init_target, **kwargs):
        """
            Setup for the PID controller

            @param init_target Initial target value for the PID value to use
            @param Kp Proportional gain 
            @param Ki Integral gain 
            @param Kd Derivative gain 
            @param Kf Feed-forward gain 
        """

        self.__Kp = Kp
        self.__Ki = kwargs.get('Ki', 0)
        self.__Kd = kwargs.get('Kd', 0)
        self.__Kf = kwargs.get('Kf', 0)
        self.__target_value = init_target
        self.__accumulated_err  = 0


    def set_setpoint(self, target):
        """
            Changes the setpoint that the controller is targeting

            @param target Target value for the PID value to use
        """
        self.__target_value = target

    def set_Kp(self, Kp):
        """
            Changes the proportional gain used by the controller

            @param Kp Proportional gain
        """
        self.__Kp = Kp

    def set_Ki(self, Ki):
        """
            Changes the integral gain used by the controller

            @param Ki Integral gain
        """
        self.__Ki = Ki

    def set_Kd(self, Kd):
        """
            Changes the derivative gain used by the controller

            @param Kd Derivative gain
        """
        self.__Kd = Kd

    def set_Kf(self, Kf):
        """
            Changes the feed-forward gain used by the controller

            @param Kf Feed-forward gain
        """
        self.__Kf = Kf

    def run(self, current_value):

        """
            Function to run an iteration of the controller

            @param current_value Current value of the system being controlled.
                Should be the same units as the target value.
        """

        error = self.__target_value - current_value

        self.__accumulated_err += error
        

        #proportional control
        kp_component = error  * self.__Kp

        ki_component = self.__accumulated_err * self.__Ki
        
        
        control_value = kp_component + ki_component
        
        return control_value