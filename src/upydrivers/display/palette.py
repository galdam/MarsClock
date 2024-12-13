"""
Following the format of RGB color encoding, palettes should use low for black (0) and high for white (1).
This should then be carried forward into the framebuffer.
From there, the device can be responsible for converting into the appropriate format.
"""

#from abc import ABC, abstractmethod


class AbsPalette(): #ABC):
    """
    Defines the colors available on a 7 color eink and 2 shades of grey.
    """
    def __init__(self):
        pass

    @staticmethod
    #@abstractmethod
    def rgb(r, g, b):
        raise NotImplementedError()

    @property
    #@abstractmethod
    def ncolors(self):
        raise NotImplementedError()

    @property
    #@abstractmethod
    def nbits(self):
        raise NotImplementedError()

    def color(self, name):
        try:
            return getattr(self, name.upper())
        except AttributeError():
            return None

    @property
    def BLACK(self):
        return self.rgb(0, 0, 0)

    @property
    def DARK_GRAY(self):
        # Hex: #505050
        return self.rgb(80, 80, 80)

    @property
    def LIGHT_GRAY(self):
        # Hex: #787878
        return self.rgb(120, 120, 120)

    @property
    def WHITE(self):
        return self.rgb(255, 255, 255)

    @property
    def RED(self):
        return self.rgb(255, 0, 0)

    @property
    def GREEN(self):
        return self.rgb(0, 255, 0)

    @property
    def BLUE(self):
        return self.rgb(0, 0, 255)

    @property
    def YELLOW(self):
        return self.rgb(255, 255, 0)

    @property
    def ORANGE(self):
        return self.rgb(255, 128, 0)


class PaletteMono(AbsPalette):
    @property
    def ncolors(self):
        return 2

    @property
    def nbits(self):
        return 1

    @staticmethod
    def rgb(r, g, b):
        # For any RGB value other than white, return black
        return 0 if any(c < 255 for c in [r, g, b]) else 1


class PaletteTricolor(AbsPalette):
    """
    Tricolor screens are generally black, white and an additional color (popular options are red or yellow).
    This palette assumes all shades other than B/W should be rendered in the third color.
    White:3, Colour: 2, Black: 1. 0 is not used.
    """
    @property
    def ncolors(self):
        return 3

    @property
    def nbits(self):
        return 2

    @staticmethod
    def rgb(r, g, b):
        t = (r + g + b)
        if t == 0:
            return 1
        if t == 255*3:
            return 3
        return 2


class PaletteGreyscale(AbsPalette):
    @property
    def ncolors(self):
        return 4

    @property
    def nbits(self):
        return 2

    @staticmethod
    def rgb(r, g, b):
        # 0: 0-42 Black
        # 1: 43-85 Dark gray
        # 2: 86-127 light gray
        # 3: 128-255 white
        return min((r + g + b) >> 7, 3)  # Greyscale in range 0 <= gs <= 3
