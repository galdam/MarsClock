import marsclock.helpers.math.mathplus as math
from marsclock.widget.abswidget import AbsWidget
from marsclock.widget.symbol import SymbolWidget, ZODIAC_SYMBOL_ORDER

class ZodiacDialWidget(AbsWidget):

    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 8,8

    def __init__(self, hardware, position, size, reverse=False, foreground_color=None, background_color=None):
        super().__init__(hardware, position, size)
        self.reverse = reverse
        self.r = min(self.size) // 2
        self.xo, self.yo = self.position[0]+self.r, self.position[1]+self.r
        self.zodiac_r = self.r-5
        #self.foreground_color = 
        #self.background_color = 'BLACK' if background_color is None else background_color

        self.colors.add_color('FG', 'WHITE' if foreground_color is None else foreground_color)
        self.colors.add_color('BG', 'BLACK' if background_color is None else background_color)

    def _draw_full(self):
        self.display.ellipse(self.xo, self.yo, self.r, self.r, self.colors['FG'], True)
        for i in range(6):
            a = math.radians((i * 30))
            x, y = int(self.r*math.cos(a)), int(self.r*math.sin(a))
            self.display.line(self.xo+x, self.yo+y,  self.xo-x, self.yo-y, self.colors['BG'])

        self.display.ellipse(self.xo, self.yo, self.r-11, self.r-11, self.colors['BG'], True)
        for i in range(6):
            a = math.radians((i * 30))
            x, y = int((self.r-11)*math.cos(a)), int((self.r-11)*math.sin(a))
            self.display.line(self.xo+x, self.yo+y,  self.xo-x, self.yo-y, self.colors['FG'])
       
        __ = """
        for i in range(6):
            a = math.radians((i * 30))
            x, y = int(self.r*math.cos(a)), int(self.r*math.sin(a))
            self.display.line(self.xo+x, self.yo+y,  self.xo-x, self.yo-y, self.colors['FG'])
        """

        m = -15 if self.reverse else -15
        o = reversed(ZODIAC_SYMBOL_ORDER) if self.reverse else ZODIAC_SYMBOL_ORDER
        for i, sy in enumerate(o):
            a = math.radians((((i+1) * 30) + m) - 90)
            SymbolWidget(self.hardware, 
                         (self.xo+int(self.zodiac_r*math.cos(a))-4, self.yo+int(self.zodiac_r*math.sin(a))-4),
                           (8,9), sy, c=self.colors.get_color_name('BG'), bg=self.colors.get_color_name('FG'),).draw(2)
            

