__ = '''
from marsclock.hardware.driver.ds3231_gen import DS3231
from marsclock.hardware.wrapper.rtc.abstract import RtcWrapperAbs


class RtcWrapperDS3231(RtcWrapperAbs):
    def __init__(self):
        self.ds3231 = DS3231()
        super().__init__()

    def _get_time_tup(self):
        return self.ds3231.get_time_tup()[:6]

    def set_time(self, tt):
        self.ds3231.set_time(tt)

'''
