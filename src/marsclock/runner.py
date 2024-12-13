
from marsclock.view.clock import ClockView
import time


def main_loop(hardware):
    active_view = ClockView(hardware, (0, 0),
                            hardware.display.width)
    while True:
        # Refresh the time
        hardware.rtc.refresh_time()

        # Run the active view
        active_view.draw()

        # Check for button presses
        active_view = swap_view(hardware, active_view)

        # Wait a beat
        time.sleep(active_view.refresh_rate)

        time.sleep(15)
        break

    # Set the seed
    # if not self.hardware.rtc.earth_time_mask.tm_hour:
    #    MetaRand.set_seed(self.hardware.rtc.earth_time.epoch_tc_hours)


def swap_view(hardware, active_view):
    # Something here triggers a new view
    return active_view
