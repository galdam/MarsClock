
from upydrivers.display.font.font_writer import Writer
from upydrivers.display.font import font_krungthep14


class FontManager:
    def __init__(self, display_device):
        self.display_device = display_device
        self.writers = {
            ('krungthep', 14): Writer(self.display_device, font_krungthep14),
        }

    def text(self, s, x, y, c, centered=False, bg=None, font=None, size=None):
        """

        Args:
            s: string
            x: x coordinate
            y: y coordinate
            c: color
            centered:
            bg:
            font:
            size:
        Returns:

        """

        writer = None if font is None else self.writers[(font, size)]
        if centered or bg:
            width = 8 * len(s) if writer else writer.stringlen(s)
            if centered:
                x = x - (width // 2)
            if bg:
                self.display_device.rect(x, y, width, size if size else 8, bg, True)
        if font is None:
            self.display_device.text(s, x, y, c)
        else:
            writer.set_textpos(self.display_device, y, x)
            writer.printstring(s, invert=True, location=(x, y))

            #self.display.krungthep_writer.set_textpos(self.display, y, x)
            #self.display.krungthep_writer.printstring(s, invert=True)




