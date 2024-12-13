
MONO_VMSB = 'MONO_VMSB'
MONO_HMSB = 'MONO_HMSB'
GS2_VMSB = 'GS2_VMSB'
GS2_HMSB = 'GS2_HMSB'


class FrameBuffer:
    def __init__(self, buffer, height, width, mode):
        pass

    def fill(self, c):
        pass

    def pixel(self, x, y, c=None):
        pass

    def hline(self, x, y, w, c):
        pass

    def vline(self, x, y, h, c):
        pass

    def line(self, x1, y1, x2, y2, c):
        pass

    def rect(self, x, y, w, h, c, f=None):
        """
        Draw a rectangle at the given location, size and color.
        The optional f parameter can be set to True to fill the rectangle.
        Otherwise just a one pixel outline is drawn.
        """
        pass

    def ellipse(self, x, y, xr, yr, c, f=None, m=None):
        pass

    def text(self, s, x, y, c=None):
        """
        Write text to the FrameBuffer using the the coordinates as the upper-left corner of the text.
        The color of the text can be defined by the optional argument but is otherwise a default value of 1.
        All characters have dimensions of 8x8 pixels and there is currently no way to change the font.
        """
        pass
