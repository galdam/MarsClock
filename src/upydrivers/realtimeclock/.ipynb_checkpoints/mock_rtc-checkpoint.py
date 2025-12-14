import time 

class RtcClockDevice:
    def __init__(self,):
        pass

    def get_time_tup(self, data=bytearray(7)):
        YY, MM, DD, hh, mm, ss, wday,__,__ = time.gmtime()
        # Time from DS3231 in time.localtime() format (less yday)
        result = YY, MM, DD, hh, mm, ss, wday, 0
        return result

    def get_time(self, data=bytearray(7)):
        result = self.get_time_tup(data)
        return time.localtime(time.mktime(result))