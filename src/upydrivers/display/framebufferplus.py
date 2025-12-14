
try:
    from framebuf import *
except ImportError:
    from mockmicro.framebuf import *

from upydrivers.display.font.bitmapfont import BitmapFont

class FrameBufferPlus(FrameBuffer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._font = None

    def text(self, s, x, y, c, font_name=None, h_spacing=None, v_spacing=None, size=None):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        #if all(v is None for v in [font_name, v_spacing, h_spacing, size]):
        #    super().text(s, x, y, c)
        #    return
        
        if font_name is None:
            font_name="font_adafruit_8x8.bin"
            if h_spacing is None: h_spacing = 0
        self.font(font_name=font_name).draw_text(self, s, x, y, c, h_spacing, v_spacing, size)
       
    def font(self, font_name=None):
        if not self._font or self._font.font_name != font_name:
            # load the font!
            self._font = BitmapFont(font_name)
        return self._font

    def rounded_rect(self, x,y, width, height, radius, c, fill):
        r = min([radius, width//2, height//2])
        
        self.ellipse(x+r, y+r, r, r, c, fill, 2)  # upper left
        self.ellipse(x+r, ((y+height)-r)-1, r, r, c, fill, 4)  # lower left
        self.ellipse(((x+width)-r)-1, y+r, r, r, c, fill, 1)  # upper right
        self.ellipse(((x+width)-r)-1, ((y+height)-r)-1, r, r, c, fill, 8)  # lower right

        if fill:
            self.rect(x+r, y, width-(r*2), height, c, fill) # vertical
            self.rect(x, y+r, width, height-(r*2), c, fill)  # horizontal
        else:
            # c = h.display.palette.RED
            self.line(x, y+r, x, ((y+height)-r)-1, c)  # left
            self.line((x+width)-1,y+r, (x+width)-1, ((y+height)-r)-1, c)  # right
            self.line(x+r,y, ((x+width)-r)-1, y, c)  # upper
            self.line(x+r, (y+height)-1, ((x+width)-r)-1, (y+height)-1, c)  # lower

    def text_box(self, s, x, y, fg, bg, r=3, margin=1, x_margin_padding=1, font_name=None, h_spacing=None, v_spacing=None, fill=True):
        if bg is not None:
            width, height = self.font(font_name).text_dim(s, h_spacing=h_spacing, v_spacing=v_spacing)
            self.rounded_rect(x-x_margin_padding-margin, y-margin, (width)+(2*x_margin_padding)+(margin*2), (height)+(margin*2),r, bg, fill)
        self.text(s, x, y, fg, font_name=font_name, h_spacing=h_spacing, v_spacing=v_spacing)



__ = '''
    def ctext(self, s, x, y, c, bg=None):
        """
        Write text to the FrameBuffer using the the coordinates
        as the upper-center corner of the text.
        """
        w = len(s) * 8
        self.bgtext(s, x-(w//2), y, c, bg)

    def bgtext(self, s, x, y, c, bg=None):
        """
        Write text to the FrameBuffer using the the coordinates as the upper-left corner of the text.
        The color of the text can be defined by the optional argument but is otherwise a default value of 1.
        All characters have dimensions of 8x8 pixels and there is currently no way to change the font.
        """
        if bg:
            w = len(s) * 8
            h = 8
            self.rect(x, y, w, h, bg, True)
        self.text(s, x, y, c)
'''


