"""
An abstract interface that defines the behaviour of a display device.
"""
# from abc import ABC, abstractmethod
import math

try:
    from machine import Pin, SPI
    import time
except ImportError:
    from mockmicro.machine import Pin, SPI
    from mockmicro import time

# from upydrivers.display import framebufferplus
import framebuf

from upydrivers.display.palette import AbsPalette


class AbstractUPyDisplayDevice(framebuf.FrameBuffer): #, metaclass=ABCMeta):
    """
    # TODO: I'm guessing a bit here, but my hope is that this set of functions are all that would need to be
    """
    _palette = None

    def __init__(self, width: int, height: int,
                 rotation: int = 0):
        """

        Args:
            width: int, number of pixels wide the display is
            height: int, number of pixels high the display is
            rotation: int, how many times to rotate the display, default: 0
        """
        # Buffer Settings
        self.rotation = rotation
        if not 0 <= rotation <= 3:
            raise ValueError(f"Rotation must be in the range 0 to 3. Value: {rotation}.")
        self.width, self.height = (width, height) if rotation % 2 == 0 else (height, width)
        if rotation > 0:
            pass
            # raise NotImplementedError("Rotation is not implemented yet")
        print(f"Size: {self.width} x {self.height}")
        self._buffer = bytearray(self.height * math.ceil(self.width / (8 // self.palette.nbits)))
        self._has_full_updates = True
        self._has_partial_updates = True
        print(f"Buffer len: {len(self._buffer)} ({self.height} * {math.ceil(self.width / (8 // self.palette.nbits))}).",
              f"Palette nBits: {self.palette.nbits}")
        # TODO: Workout if this works with the H/V modes. Some additional transformations may need to be done
        super().__init__(self._buffer, self.width, self.height, self.framebuf_mode)

    def shutdown(self):
        raise NotImplementedError()

    @property
    def palette(self) -> AbsPalette:
        if self._palette is None:
            raise NotImplementedError()
        return self._palette

    @property
    #@abstractmethod
    def framebuf_mode(self):
        """"""
        raise NotImplementedError()

    @property
    def has_update(self):
        return self._has_full_updates or self._has_partial_updates

    def apply_full_update(self):
        self._has_full_updates = True

    def apply_partial_update(self):
        self._has_partial_updates = True

    #@abstractmethod
    def show(self):
        raise NotImplementedError()

    @property
    #@abstractmethod
    def ready(self):
        raise NotImplementedError()

    def _wait_until_ready(self, wait_before=0):
        time.sleep_ms(wait_before)
        while not self.ready:
            time.sleep_ms(100)

    @staticmethod
    def _sleep_ms(t):
        # I'm being lazy - I just don't want to do the messy time import for all implementations
        time.sleep_ms(t)

    def enable_partial_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        pass

    def enable_full_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        pass

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
