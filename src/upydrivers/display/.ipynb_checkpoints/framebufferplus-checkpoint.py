
try:
    import framebuf
except ImportError:
    from mockmicro import framebuf


class FrameBufferPlus(framebuf.FrameBuffer):
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
