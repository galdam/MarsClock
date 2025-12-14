from marsclock.widget.abswidget import AbsWidget

ZODIAC_SYMBOL_ORDER =['Ari', 'Tau', 'Gem', 'Cnc',
                      'Leo', 'Vir', 'Lib', 'Sco',
                      'Sgr', 'Cap', 'Aqr', 'Psc']

PLANET_SYMBOL_ORDER =  [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Earth', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune',]

class SymbolWidget(AbsWidget):
    _SYMBOL_MAP = {
        'Sun': 'A', 'Mercury': 'B', 'Venus': 'C', 'Earth': 'D',  'Mars': 'E',
        'Jupiter': 'F', 'Saturn': 'G', 'Uranus': 'H', 'Neptune': 'I', 'Moon': 'J',
        'Ari': 'K', 'Tau': 'L', 'Gem': 'M', 'Cnc': 'N',
        'Leo': 'O', 'Vir': 'P', 'Lib': 'Q', 'Sco': 'R',
        'Sgr': 'S', 'Cap': 'T', 'Aqr': 'U', 'Psc': 'V'
    }

    #SYMBOLS = list(_SYMBOL_MAP.keys()) 

    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 8,8

    def __init__(self, hardware, position, size, symbol, c=None, bg=None, draw_bg=False):
        super().__init__(hardware, position, size)
        self.symbol = symbol

        if draw_bg or bg:
            self.draw_bg = True
            self.colors.add_color('FG', 'WHITE' if c is None else c)
            self.colors.add_color('BG', 'RED' if bg is None else bg)
        else:
            self.draw_bg = False
            self.colors.add_color('FG', 'BLACK' if c is None else c)

    def _draw_full(self):
        if self.draw_bg:
            self.display.rect(self.x, self.y, 9, 8, self.colors['BG'], True)
            self.display.line(self.x+1, self.y-1, self.x+7, self.y-1, self.colors['BG']) # Up
            self.display.line(self.x+1, self.y+8, self.x+7, self.y+8, self.colors['BG']) # Down
            self.display.line(self.x-1, self.y+1, self.x-1, self.y+6, self.colors['BG']) # Left
            self.display.line(self.x+9, self.y+1, self.x+9, self.y+6, self.colors['BG']) # Right
        self.display.text(self._SYMBOL_MAP[self.symbol], self.x, self.y, self.colors['FG'], font_name='font_zodiac_8.bin')


class SymbolKeyWidget(AbsWidget):

    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 150, 124

    def __init__(self, hardware, position, size, c=None, bg=None):
        super().__init__(hardware, position, size)
        self.colors.add_color('FG', 'WHITE' if c is None else c)
        self.colors.add_color('BG', 'RED' if bg is None else bg)

        for (x, y), sy in self._zodiac_iterator():
            self.add_subwidget(
                SymbolWidget(self.hardware, (x, y), (8,9), sy, 
                             c=self.colors.get_color_name('FG'), 
                             bg=self.colors.get_color_name('BG')))
            
    def _draw_full(self):
        for (x, y), sy in self._zodiac_iterator():
            self.display.text(sy, x+12, y, self.colors['BG'])

    def _zodiac_iterator(self):
        xo, yo = self.position
        xo, yo = xo + 4, yo + 4

        for i in range(5):
            y = yo + (i * 12)
            for j in range(2):
                x = xo+(75*j)
                sy = PLANET_SYMBOL_ORDER[i+(j*5)]
                yield (x,y), sy
                #SymbolWidget(self.hardware, (x, y), (8,9), sy, c=self.colors.get_color_name('FG'), bg=self.colors.get_color_name('BG')).draw()
                #self.display.text(sy, x+12, y, self.colors['BG'])
                
        for i in range(4):
            y = yo + (6*12) + (i * 12)
            for j in range(3):
                x = xo+(50*j)
                sy = ZODIAC_SYMBOL_ORDER[i+(j*4)]
                yield (x,y), sy
                #SymbolWidget(self.hardware, (x, y), (8,9), sy, c=self.colors.get_color_name('FG'), bg=self.colors.get_color_name('BG')).draw()
                #self.display.text(sy, x+12, y, self.colors['BG'])

    __ = '''
    def _draw(self):
        xo, yo = self.position
        xo, yo = xo + 4, yo + 4

        for i in range(5):
            y = yo + (i * 12)
            for j in range(2):
                x = xo+(75*j)
                sy = PLANET_SYMBOL_ORDER[i+(j*5)]
                SymbolWidget(self.hardware, (x, y), (8,9), sy, c=self.colors.get_color_name('FG'), bg=self.colors.get_color_name('BG')).draw()
                self.display.text(sy, x+12, y, self.colors['BG'])
                
        for i in range(4):
            y = yo + (6*12) + (i * 12)
            for j in range(3):
                x = xo+(50*j)
                sy = ZODIAC_SYMBOL_ORDER[i+(j*4)]
                SymbolWidget(self.hardware, (x, y), (8,9), sy, c=self.colors.get_color_name('FG'), bg=self.colors.get_color_name('BG')).draw()
                self.display.text(sy, x+12, y, self.colors['BG'])

        # self.display.rect(*self.position, *self.minimum_size, self.colors['BG'])
        '''
