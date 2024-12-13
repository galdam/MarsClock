__ = '''
import time
from marsclock.hardware.wrapper.rtc.abstract import RtcWrapperAbs


class RtcWrapperMacropy(RtcWrapperAbs):
    def set_time(self, tt):
        pass

    def _get_time_tup(self):
        return time.gmtime()[:6]

'''