
import time

from marsclock.view.welcome import WelcomeView
from marsclock.view.clock import ClockView
from marsclock.view.geocentric import GeocentricView
from marsclock.view.heliocentric import HeliocentricView
from marsclock.view.asterism import AsterismView
from marsclock.helpers.math.random import MetaRand

__ = '''
def main_loop(hardware): 
    for active_view in [ClockView, GeocentricView, ClockView, HeliocentricView, ClockView]:
        # Refresh the time
        hardware.rtc.refresh_time()

        # Run the active view
        active_view(hardware)
        active_view.draw()

        # Check for button presses
        #active_view = swap_view(hardware, active_view)
        hardware.display.apply_full_update()
        hardware.draw()
        # Wait a beat
        #time.sleep(active_view.refresh_rate)

        time.sleep(20)
    hardware.display.shutdown()
'''

def main_loop(hardware):

    # Draw the welcome screen 
    hardware.set_view(WelcomeView)
    hardware.tick()
    hardware.cycle()
    time.sleep(10)

    # If a button has been pressed
    #    Move into settings view

    last_change = None

    while True:
        hardware.tick()
        if last_change != (hardware.rtc.mars_time.tm_min // 10):
            last_change = hardware.rtc.mars_time.tm_min // 10
            hardware.set_view(swap_view(last_change))
        # Refresh the time 
        hardware.cycle()
        
        time.sleep(20)

        #((not self.hardware.rtc.earth_time_mask.tm_hour) 

        # Run the active view
        #active_view.draw()

        # Check for button presses
        #active_view = swap_view(hardware, active_view)
        #hardware.display.apply_full_update()
        #hardware.draw()
        # Wait a beat
        #time.sleep(active_view.refresh_rate)

        #time.sleep(15)


def swap_view(i):
    #i = MetaRand.rand_int(10)
    views = {
        0: ClockView,
        1: ClockView,
        2: AsterismView,
        3: AsterismView,
        4: GeocentricView,
        5: HeliocentricView,
    }
    return views[i]

