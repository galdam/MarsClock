from marsclock.astro import ephemeris, ephemerisrelative

from marsclock.widget.abswidget import AbsWidget
from marsclock import config



class AscensionTimesWidget(AbsWidget):
   
    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 112, 8

    def __init__(self, hardware, position: tuple[int, int], size: tuple[int, int], target=None):
        """

        Args:
            hardware:
            position:
            size:
        """
        super().__init__(hardware, position, size)
        self.colors.add_color('BG', 'WHITE')
        self.colors.add_color('TEXT', 'BLACK')
        self.target=target

        self.next_twilights = self.calculate_next_twilights()

    def calculate_next_twilights(self):
        et = self.hardware.rtc.earth_time
        location = config.EARTH_LOCATION
        et_kwargs={'tm_tzone': et.tm_tzone}

        er = ephemerisrelative.EphemerisRelative(
                observer='Earth',
                target=self.target,
                j2k=et.j2kdelta,
                location=location,
                et_kwargs=et_kwargs
            )
        return er.next_twilights()
    
    @property
    def _has_update(self):
        if not self.hardware.rtc.earth_time_mask.tm_mday:
            return 2
        if self.next_twilights is not None:
            if self.next_twilights[0][1] <= self.hardware.rtc.earth_time:
                return 2
        return 0


    def _draw_full(self):
        # Only recalculate the next rise/set time if it's unset of the current time is greater
        if (self.next_twilights is None) | (self.next_twilights[0][1] <= self.hardware.rtc.earth_time):
            self.next_twilights = self.calculate_next_twilights()

        if self.next_twilights is None:
            return
        x, y = self.position
        sigil_w = 15

        self.draw_sigil(x, y, self.colors['TEXT'], self.colors['BG'], is_rise=self.next_twilights[0][0] == 'rise')

        text = ' | '.join([t.fmt_time() for s, t in self.next_twilights])
        self.display.text(text, x+sigil_w+3, y+2, self.colors['TEXT'], font_name='font_adafruit_5x8.bin', v_spacing=1)

        self.draw_sigil(x+(len(text)*6)+sigil_w+5, y, self.colors['TEXT'], self.colors['BG'], 
                        is_rise=self.next_twilights[1][0] == 'rise')


    def draw_sigil(self, x, y, c, bg, is_rise=True):
        # 14w x 8h
        dd = self.display
        r = 5
        xo, yo = x+r+2, y+(r+3)

        f = False if is_rise else True
        # Draw the semi-circle
        dd.ellipse(xo, yo, r, r, c ,f, 3)

        # Draw the horizon
        dd.line(xo-(r+2), yo, xo-(r-1), yo, c)
        dd.line(xo+(r+2), yo, xo+(r-1), yo, c)

        # Draw an arrow pointing up or down depending on the direction
        if is_rise:
            dd.line(xo-(r-3), yo, xo, yo-2, c)
            dd.line(xo+(r-3), yo, xo, yo-2, c)
        else:
            dd.line(xo-(r-3), yo-2, xo, yo, bg)
            dd.line(xo+(r-3), yo-2, xo, yo, bg)
            
        #dd.line(xo, yo-(r+2), xo, yo-(r+3), c)
        #dd.line(x-(r+2), y-(r+2), x-(r+3), y-(r+3), c)

        # Draw sun rays or mars symbol
        if self.target is None:
            dd.line(xo, yo-(r+2), xo, yo-(r+3), c)
            dd.line(xo-((r//2)+3), yo-((r//2)+3), xo-((r//2)+4), yo-((r//2)+4), c)
            dd.line(xo+((r//2)+3), yo-((r//2)+3), xo+((r//2)+4), yo-((r//2)+4), c)
        else:
            px, py = xo+((r//2)+5), yo-((r//2)+5)
            dd.line(xo+((r//2)+2), yo-((r//2)+2), px, py, c)
            dd.line(px-2, py, px, py, c)
            dd.line(px, py+2, px, py, c)

