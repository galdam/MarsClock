from upydrivers import upylog
from marsclock.astro.astrotimestrfmt import StrFmtTime
from marsclock.widget.abswidget import AbsWidget

from marsclock.widget.heliocentricearthmars import HeliocentricEarthMarsWidget
from marsclock.widget.moonphase import MoonPhaseWidget
from marsclock.widget.ascensiontimes import AscensionTimesWidget

TIME_FMTS = [
    StrFmtTime("%A"),  # f'{day_name}',
    StrFmtTime("%d %B"),  # f'{dt.tm_mday} {month_name}',
    StrFmtTime("%H:%M"),  # f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}',#:{dt.tm_sec:0>2d}',
    StrFmtTime("%Y/%m/%d"),  # f'{dt.tm_year}/{dt.tm_mon:0>2d}/{dt.tm_mday:0>2d}',
]


class DateBarWidget(AbsWidget):

    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: tuple[int, int], width, height,
        """
        return 400, 80 

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
        self.colors.add_color('LINE', 'RED')

        self._bar_width = 400
        self._center = self.width // 2  # self._bar_width // 2

        solar_size = self.height
        solar_radius = int(solar_size / 2)
        solar_position = (self._center - solar_radius), self.y

        self.upper_line = self.y + ((self.height-70) // 2)

        self.add_subwidget(
            HeliocentricEarthMarsWidget(
                hardware, solar_position, (solar_size, solar_size)))
        
        ascension_y = self.upper_line + 58 # 68 #112
        self.ascension_x = 34
        self.add_subwidget(
            AscensionTimesWidget(hardware, (self.ascension_x, ascension_y), (112, 10), target=None))
        
        self.add_subwidget(
            AscensionTimesWidget(hardware, (400-(self.ascension_x+112), ascension_y), (112, 10), target='Mars'))
        
        #self.add_subwidget(
        #    MoonPhaseWidget(hardware, (20, self.upper_line+6), (10, 10), outer=True))
        self.add_subwidget(
            MoonPhaseWidget(hardware, (20, self.upper_line+6), (15, 15), outer=True))
    
    @property
    def _has_update(self):
        if ((not self.hardware.rtc.earth_time_mask.tm_hour) 
                or (not self.hardware.rtc.mars_time_mask.tm_hour)):
            upylog.debug('[DateBarWidget] Full update requested')
            return 2
        if ((not self.hardware.rtc.earth_time_mask.tm_min) 
                or (not self.hardware.rtc.mars_time_mask.tm_min)):
            upylog.debug('[DateBarWidget] Partial update requested')
            return 1
        upylog.debug('[DateBarWidget] No update requested')
        return 0

    def _draw_full(self):
        # The hours have changed
        h = ((self.height-80) // 2) + 72
        self.display.rect(self.x,self.y, self.width, h, self.colors['BG'], True)
        self._draw_mirrored_dates('Earth', align_left=True, update_type=2)
        self._draw_mirrored_dates('Mars', align_left=False, update_type=2)

    def _draw_partial(self):
        # The minutes have changed
        self._draw_mirrored_dates('Earth', align_left=True, update_type=1)
        self._draw_mirrored_dates('Mars', align_left=False, update_type=1)


    def _draw_mirrored_dates(self, planet, align_left:bool, update_type):
        margin = 16
        padding_chars=16
        a = '>' if align_left else '<'
        padding_formatter = f'{a}{padding_chars}'
        padding_format = '{:'+padding_formatter+'}'

        if planet == 'Earth':
            dt = [fmt.format_time(self.hardware.rtc.earth_time)
                        for fmt in TIME_FMTS]
        elif planet == 'Mars':
            dt = [fmt.format_time(self.hardware.rtc.mars_time)
                   for fmt in TIME_FMTS]
        else:
            raise ValueError(f'Planet not recognised: {planet}')
        
        text_x = margin if align_left else self.width - (margin + (padding_chars * 8))

        if update_type == 2:
            #y = 10
            y = self.upper_line

            self.display.rounded_rect(margin, y-1, self.width-(margin*2), 3, 2, self.colors['LINE'], True)
            #self._draw_horizontal_line(margin, self._center, y, align_left)

            # Day of week
            # y = 14
            y = self.upper_line + 4
            self.display.text(padding_format.format(dt[0]), text_x, y, self.colors['TEXT'])

            # Day of month and month
            #y = 24
            y = self.upper_line + 14
            self.display.text(padding_format.format(dt[1]), text_x, y, self.colors['TEXT'])

        c = (self.ascension_x + (112//2))
        if not align_left:
            c = 400 - c
        
        #y = 36
        y = self.upper_line + 28
        d = (len(dt[2]) * 12)
        f = c - (d//2)
        # Blank out the background for a partial update
        if update_type == 1:
            self.display.rect(f, y, d, 14, self.colors['BG'], True)

        self.display.text(dt[2], f, y, self.colors['TEXT'], 
                         font_name='font_krungthep_14.bin')

        if update_type == 2:
            y = self.upper_line + 48
            #y = 65 # 70-(8+7)
            d = (len(dt[3]) * 8)
            f = c - (d//2)
            self.display.text(dt[3], f, y, self.colors['TEXT'])
            y = self.upper_line+70

            self.display.rounded_rect(margin, y-1, self.width-(margin*2), 3, 2, self.colors['LINE'], True)
            #self._draw_mirrored_hline(margin, self._center, y)

    def _write_centered_str(self, center_x, y, text):
        x = int(center_x - ((13 * len(text)) / 2))
        self.display.krungthep_writer.set_textpos(self.display, y, x)
        self.display.krungthep_writer.printstring(text, invert=True)

    def _draw_horizontal_line(self, x1, x2, y, align_left):
        if align_left:
            self.display.line(x1, y, x2, y, self.colors['LINE'])
        else:
            self.display.line(self.width - x1, y, self.width - x2, y, self.colors['LINE'])

    def _draw_mirrored_hline(self, x1, x2, y):
        self._draw_horizontal_line(x1, x2, y, align_left=True)
        self._draw_horizontal_line(x1, x2, y, align_left=False)
