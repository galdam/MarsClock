from marsclock.hardware.wrapper.display.abstract import DisplayWrapperAbs
from marsclock.hardware.driver import epaper


class DisplayWrapperEpd(DisplayWrapperAbs):
    def __init__(self):
        self._epd = epaper.EPD()
        self._partial_refresh_count = 0
        super().__init__()

    def update_screen(self, full=False):
        if not full and self._partial_refresh_count < 30:
            self._epd.set_partial_update()
            self._partial_refresh_count += 1
        else:
            self._epd.set_full_update()
            self._partial_refresh_count = 0
        self._epd.show()


    def shutdown(self):
        self._epd.set_full_update()
        self._epd.clear()
        self._epd.sleep()
