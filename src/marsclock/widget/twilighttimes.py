from marsclock.astro import ephemeris, ephemerisrelative

from marsclock.widget.abswidget import AbsWidget
from marsclock import config

class TwilightTimesWidget(AbsWidget):
   
    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 136, 8

    def __init__(self, hardware, position: tuple[int, int], size: tuple[int, int]):
        """

        Args:
            hardware:
            position:
            size:
        """
        super().__init__(hardware, position, size)
        self.colors.add_color('BG', 'WHITE')
        self.colors.add_color('TEXT', 'BLACK')

    def calculate_next_twilights(self):
        et = self.hardware.rtc.earth_time
        location = config.EARTH_LOCATION
        et_kwargs={'tm_tzone': et.tm_tzone}

        er = ephemerisrelative.EphemerisRelative(
                observer='Earth',
                j2k=et.j2kdelta,
                location=location,
                et_kwargs=et_kwargs
            )
        return er.next_twilights()
        #if next_twilights is None:
        #    return None
        #returnnext_twilights
        #sigil_lkup = {'set': '', 'rise': 'A'}


        #twilight_txt = ' | '.join([f"{sigil_lkup[s]} {t.fmt_time()}" for s, t in next_twilights])
        #return twilight_txt

    def _draw_full(self):
        next_twilights = self.calculate_next_twilights()
        if next_twilights is None:
            return
        x, y = self.position
        sigil_y_shift=7

        self.draw_sigil(x+5, y+sigil_y_shift, self.colors['TEXT'], self.colors['BG'], is_rise=next_twilights[0][0] == 'rise')

        text = ' | '.join([t.fmt_time() for s, t in next_twilights])
        self.display.text(text, x+20, y, self.colors['TEXT'], font_name='font_adafruit_5x8.bin', v_spacing=1)

        self.draw_sigil(x+11+(len(text)*8), y+sigil_y_shift, self.colors['TEXT'], self.colors['BG'], 
                        is_rise=next_twilights[1][0] == 'rise')
        

    def draw_sigil(self, x, y, c, bg, is_rise=True):
        dd = self.display
        #x, y = 200, 200
        r = 5
        f = False if is_rise else True
        dd.ellipse(x, y, r, r, c ,f, m=3)
        
        dd.line(x-(r+2), y, x-(r-1), y, c)
        dd.line(x+(r+2), y, x+(r-1), y, c)

        #dd.line(x-(r+2), y, x+(r+2), y, c)

        if is_rise:
            dd.line(x-(r-3), y, x, y-2, c)
            dd.line(x+(r-3), y, x, y-2, c)
        else:
            dd.line(x-(r-3), y-2, x, y, bg)
            dd.line(x+(r-3), y-2, x, y, bg)
            
        dd.line(x, y-(r+2), x, y-(r+3), c)
        
        #dd.line(x-(r+2), y-(r+2), x-(r+3), y-(r+3), c)
        dd.line(x, y-(r+2), x, y-(r+3), c)
        dd.line(x-((r//2)+3), y-((r//2)+3), x-((r//2)+4), y-((r//2)+4), c)
        dd.line(x+((r//2)+3), y-((r//2)+3), x+((r//2)+4), y-((r//2)+4), c)

