import os
from marsclock.helpers.math.random import MetaRand
from marsclock.config import RESOURCE_PATH
from marsclock.widget.abswidget import AbsWidget
import json



ASTERISM_RESOURCE_PATH = '/'.join([RESOURCE_PATH, 'asterisms'])


class AsterismWidget(AbsWidget):
    @property
    def minimum_size(self) -> tuple[int, int]:
        return 400, 200
    
    def __init__(self, hardware, position, size):
        super().__init__(hardware, position, size)
        self.colors.add_color('BG', 'BLACK')
        self.colors.add_color('STAR', 'WHITE')
        self.colors.add_color('LINE', 'WHITE')
        self.asterism_path = None

    def _draw_full(self):
        if self.asterism_path is None:
            self.asterism_path = self._select_random_asterism()
        self._draw_asterisms(self.asterism_path)

    def _select_random_asterism(self):
        asterism_paths = ['/'.join([ASTERISM_RESOURCE_PATH, p]) for p in os.listdir(ASTERISM_RESOURCE_PATH) if p.endswith('.json')]
        n = MetaRand.rand_int(len(asterism_paths))
        return asterism_paths[n]

    def _draw_asterisms(self, asterism_path):
        chart = json.load(open(asterism_path))
        xo, yo = 0, 83
        self.display.rect(0,yo,400,300-yo,self.colors['BG'],True)

        for (x1, y1), (x2, y2), __ in chart['Asterisms']:
            self.display.line(xo+x1, yo+y1, xo+x2, yo+y2, self.colors['LINE'])
        
        mag = 3.5
        mag_max = 4.8
        r = 2
        for (x, y), m in chart['Stars']:
            if m < mag:
                self.display.ellipse(xo+x, yo+y, r+2, r+2,  self.colors['BG'], True)
            elif m < mag_max:
                self.display.ellipse(xo+x, yo+y, 3, 3,  self.colors['BG'], True)
        
        for (x, y), m in chart['Stars']:
            if m < mag:
                self.display.ellipse(xo+x, yo+y, r, r, self.colors['STAR'], True)
            elif m < mag_max:
                self.display.ellipse(xo+x, yo+y, 1, 1, self.colors['STAR'], True)
                
        for (x, y), n, iau in chart['AsterismNames']:
            n = n.replace(' ', '\n')
            self.display.text(n, xo+x, yo+y, self.colors['LINE'], font_name='font_adafruit_5x8.bin', v_spacing=1)

