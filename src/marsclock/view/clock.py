import time
#from marsclock.helpers.math.random import MetaRand
# from marsclock.astro import astrotime
from marsclock.astro.strfmtastrotime import StrFmtTime
#from marsclock.widget.solar import SolarWidget
#from marsclock.widget.bulletin import BulletinWidget
#from marsclock.widget.moonphase import MoonPhaseWidget


from marsclock.view.absview import AbsView
from marsclock.widget.datebar import DateBarWidget
#from marsclock.widget.bulletin import BulletinWidget


class ClockView(AbsView):
    def __init__(self, hardware, position, size):
        super().__init__(hardware, position, size)

        ## Solar Widget
        #solar_size = 80
        #solar_position = 200 - (solar_size // 2), 5

        self.add_widget(
            DateBarWidget(self.hardware, (0, 0), self.display.width))
        #self.add_widget(
        #    BulletinWidget(self.hardware, (0, 0), self.display.width))


        #self.widgets.append(SolarWidget(self, solar_size, solar_position),)
        #self.widgets.append(BulletinWidget(self, 0, 0))
        #self.widgets.append(MoonPhaseWidget(self, 16, (20, 20)))
        __ = '''
        self.time_formatters = [
            StrFmtTime("%A"),  # f'{day_name}',
            StrFmtTime("%d %B"),  # f'{dt.tm_mday} {month_name}',
            StrFmtTime("%H:%M"),  # f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}',#:{dt.tm_sec:0>2d}',
            StrFmtTime("%Y/%m/%d"),  # f'{dt.tm_year}/{dt.tm_mon:0>2d}/{dt.tm_mday:0>2d}',
        ]'''
