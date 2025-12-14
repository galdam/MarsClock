"""
An abstract interface that defines the behaviour of a display device.
"""
# from abc import ABC, abstractmethod
import math

try:
    from machine import Pin, SPI
    import time
    #import framebuf
except ImportError:
    from mockmicro.machine import Pin, SPI
    from mockmicro import time
    #from mockmicro import framebuf

from upydrivers import upylog
from upydrivers.display.framebufferplus import FrameBufferPlus
from upydrivers.display.palette import AbsPalette
#from upydrivers.display.font.bitmapfont import BitmapFont


class AbstractUPyDisplayDevice(FrameBufferPlus): #, metaclass=ABCMeta):
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
            raise ValueError("Rotation must be in the range 0 to 3. Value: {}.", rotation)
        self.width, self.height = (width, height) if rotation % 2 == 0 else (height, width)
        #if rotation > 0:
        #    pass
        #    # raise NotImplementedError("Rotation is not implemented yet")
        upylog.info("[DisplayDevice.init] Size: {} x {}", self.width, self.height)
        upylog.info("[DisplayDevice.init] Palette nBits: {}", self.palette.nbits)
        
        buffer_len = self.height * math.ceil(self.width / (8 // self.palette.nbits))
        upylog.info("[DisplayDevice.init] Buffer len: {} bytes (h:{} * ceil(w:{} / (8 // nbits:{}))",
                    buffer_len, self.height, self.width, self.palette.nbits)
        self._buffer = bytearray(buffer_len)
        #self._updates = 2
        #self._has_full_updates = True
        #self._has_partial_updates = True
        self._font = None

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

    __ = '''
    @property
    def has_update(self):
        return self._has_full_updates or self._has_partial_updates

    def apply_full_update(self):
        self._has_full_updates = True

    def apply_partial_update(self):
        self._has_partial_updates = True'''

    #@abstractmethod
    def show(self, force):
        raise NotImplementedError()

    @property
    #@abstractmethod
    def ready(self):
        raise NotImplementedError()

    def _wait_until_ready(self, wait_before=0):
        upylog.trace('[DisplayDevice._wait_until_ready]')
        time.sleep_ms(wait_before)
        while not self.ready:
            time.sleep_ms(100)
    
    __ = '''
    @staticmethod
    def _sleep_ms(t):
        # I'm being lazy - I just don't want to do the messy time import for all implementations
        time.sleep_ms(t)
    '''

    @property
    def partial_updates_supported(self):
        return False

    def enable_partial_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        pass

    def enable_full_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        pass

    def clear(self):
        # Clear the display
        upylog.trace('[DisplayDevice.clear]')
        self.fill(self.palette.WHITE)
