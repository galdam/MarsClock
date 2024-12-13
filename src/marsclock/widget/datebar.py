from marsclock.astro.strfmtastrotime import StrFmtTime
from marsclock.widget.abswidget import AbsWidget

from marsclock.widget.heliocentricearthmars import HeliocentricEarthMarsWidget

TIME_FMTS = [
    StrFmtTime("%A"),  # f'{day_name}',
    StrFmtTime("%d %B"),  # f'{dt.tm_mday} {month_name}',
    StrFmtTime("%H:%M"),  # f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}',#:{dt.tm_sec:0>2d}',
    StrFmtTime("%Y/%m/%d"),  # f'{dt.tm_year}/{dt.tm_mon:0>2d}/{dt.tm_mday:0>2d}',
]


class DateBarWidget(AbsWidget):
    def __init__(self, hardware, position, size):
        super().__init__(hardware, position, size)
        self.colors.add_color('BG', 'WHITE')
        self.colors.add_color('TEXT', 'BLACK')
        self.colors.add_color('LINE', 'RED')

        self.width = 400
        self.center = self.width // 2

        solar_size = 80
        solar_radius = int(solar_size / 2)
        solar_position = (self.center - solar_radius), self.position[1]
        self.add_widget(HeliocentricEarthMarsWidget(hardware, solar_position, solar_size))

    def _draw(self):
        self.display.apply_partial_update()
        self._draw_mirrored_dates('Earth', left=True)
        self._draw_mirrored_dates('Mars', left=False)

    def _draw_mirrored_dates(self, planet, left):
        margin = 16
        a = '>' if left else '<'

        __ = '''
        if planet == 'earth':
            dt = [fmt.format_time(self.hardware.rtc.earth_time)
                        for fmt in TIME_FMTS]
        else:
            dt = [fmt.format_time(self.hardware.rtc.mars_time)
                   for fmt in TIME_FMTS]
        '''
        ltext = margin
        #rtext = 400 - (ltext + (16 * 8))

        text_x = margin if left else self.width - (margin + (16*8))

        y = 10
        self._draw_horizontal_line(margin, self.center - 30, y, left)

        y = 20
        #self.display.text('{:{a}16}'.format(dt[0], a=a), text_x, y, self.colors['TEXT'])

        y = 30
        #self.display.text('{:{a}16}'.format(dt[1], a=a), text_x, y, self.colors['TEXT'])

        y = 60
        #c_x = ltext + (((200 - 30)-ltext)/2)
        #self._write_centered_str(c_x, y, earth_dt[3])
        #self._write_centered_str(400 - c_x, y, mars_dt[3])

        y = 80
        self._draw_mirrored_hline(ltext, self.center - 30, y)

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
