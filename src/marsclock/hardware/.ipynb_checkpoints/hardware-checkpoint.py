"""
A class that handles the collection of hardware interface instances.
"""
#from marsclock.astro import astrotime
#from marsclock.mathutils import MetaRand


from upydrivers.display.displaydevice import AbstractUPyDisplayDevice
from marsclock.hardware.rtcdevice import RtcWrapper

#try:
#    from marsclock.hardware.wrapper.rtc.ds3231 import RtcWrapperDS3231 as Rtc
#except ImportError as err:
#    from marsclock.hardware.wrapper.rtc.macropy import RtcWrapperMacropy as Rtc


class Hardware:
    def __init__(self, display: AbstractUPyDisplayDevice, rtc):
        self.display = display
        self.rtc = RtcWrapper(rtc)
        #self.buttons = None

    def shutdown(self):
        print('Hardware shutting down.')
        self.display.shutdown()

    def draw(self):
        if self.display.has_update:
            self.display.show()
