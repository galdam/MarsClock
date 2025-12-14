"""
A class that handles the collection of hardware interface instances.
"""
#from marsclock.astro import astrotime
#from marsclock.mathutils import MetaRand


from upydrivers.display.displaydevice import AbstractUPyDisplayDevice
from marsclock.hardware.rtcdevice import RtcWrapper
from marsclock.helpers.math.random import MetaRand
from upydrivers import upylog

#try:
#    from marsclock.hardware.wrapper.rtc.ds3231 import RtcWrapperDS3231 as Rtc
#except ImportError as err:
#    from marsclock.hardware.wrapper.rtc.macropy import RtcWrapperMacropy as Rtc

FULL = 2
PARTIAL = 1
NOUPDATE = 0

class Hardware:
    def __init__(self, display: AbstractUPyDisplayDevice, rtc, buttons=None):
        self.display = display
        self.rtc = RtcWrapper(rtc)
        self.view = None
        self.updates = FULL
        #self.buttons = None

    def shutdown(self):
        print('Hardware shutting down.')
        self.display.shutdown()

    def set_view(self, view):
        self.rtc.refresh_time()
        MetaRand.set_seed(self.rtc.earth_time.epoch_tc_hours)
        self.view = view(self)
        self.updates = FULL
        self.display.clear()

    def tick(self):
        upylog.trace('[Hardware.cycle]')
        self.rtc.refresh_time()
        upylog.debug('[Hardware.cycle] Earth: {},  Mars: {}', self.rtc.earth_time, self.rtc.mars_time)
        print('Y M D h m s')
        print(' '.join(['-' if v else 'X' for v in self.rtc.earth_time_mask]), '  Earth')
        print(' '.join(['-' if v else 'X' for v in self.rtc.mars_time_mask]), '  Mars')

        
    def cycle(self):
        # Set the seed
        if not self.rtc.earth_time_mask.tm_hour:
            MetaRand.set_seed(self.rtc.earth_time.epoch_tc_hours)
        children_update_type = self.view.has_update
        upylog.debug('[Hardware.cycle] Updates Status. Children: {}, Hardware: {}', children_update_type, self.updates)
        updates = max(self.updates, children_update_type)
        if updates == NOUPDATE:
            return
        if updates == PARTIAL and self.display.partial_updates_supported:
            self.display.enable_partial_updates()
            self.view.draw(PARTIAL)
        else:
            self.display.clear()
            self.display.enable_full_updates()
            self.view.draw(FULL)
        self.display.show()
        self.updates = NOUPDATE
        self.view.action()
