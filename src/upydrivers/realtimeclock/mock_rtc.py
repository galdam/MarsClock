import time 

class RtcClockDevice:
    def __init__(self, timedelta=0):
        self.timedelta = timedelta

    def get_time_tup(self, data=bytearray(7)):
        t = time.gmtime(time.mktime(time.gmtime()) + self.timedelta)
        YY, MM, DD, hh, mm, ss, wday = t[:7]
        #YY, MM, DD, hh, mm, ss, wday,__,__ = time.gmtime()
        # Time from DS3231 in time.localtime() format (less yday)
        result = YY, MM, DD, hh, mm, ss, wday, 0
        return result

    def get_time(self, data=bytearray(7)):
        result = self.get_time_tup(data)
        return time.localtime(time.mktime(result))