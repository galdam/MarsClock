#from abc import ABCMeta, abstractmethod


from PIL import Image

from mockmicro.machine import Pin, SPI
from mockmicro import time

from upydrivers.display import palette
from upydrivers.display.displaydevice import AbstractUPyDisplayDevice
from upydrivers.display.byteoperations import deinterlace_bytearray, rotate_msb_bytearray
import upydrivers.display.framebufferplus as framebuf
from upydrivers import upylog


def data_iterator(data):
    for d in data:
        yield d


BUF1 = bytearray(1)


SCALE=2



def buffer_2_pilimg(fb, scale=SCALE):
    if fb.palette.ncolors == 2:
        palette = {
            0: (10, 10, 10), # Black
            1: (230, 230, 230), # white
        }

    elif fb.palette.ncolors == 3:
        palette = {3: (230, 230, 230), # white
                2: (230, 0, 0),  # Red
                1: (10, 10, 10), # Black
                }
    else:
        raise NotImplementedError()
    a = scale
    img_size = (fb.display_width*a, fb.display_height*a)
    img = Image.new( 'RGB', img_size, "green") # Create a new image
    pixels = img.load() # Create the pixel map

    #print(fb.height, 'x', fb.width)
    #print(fb.display_height, 'x', fb.display_width)
    #for y in range(max(fb.height, fb.width)): #range(fb.height):
    #    for x in range(max(fb.height, fb.width)): #range(fb.width):
    
    for y in range(fb.display_height): #range(fb.height):
        for x in range(fb.display_width): #range(fb.width):
            c = palette[fb.pixel(x, y)]
            for i in range(a):
                for j in range(a):
                    pixels[(x*a)+i,(y*a)+j] = c
    return img

#def clear_buffer():
#    fb.fill(WHITE)


class IcDevice(AbstractUPyDisplayDevice):#, metaclass=ABCMeta):
    """
    Common class that defines the basic interface for the IC drivers.
    The basic usage loop is:
    1. initialise_configuration (display size, scan direction etc)
    2. send image data to the RAM <- outside the scope of this class
    3. display_refresh
        a. PON (Power on)
        b. DRF (Display refresh)
        c. POF (Power off)
        d. OPTIONALLY: DSLP (deep sleep)
    If deep sleep is entered, the start from the top,
    Otherwise, the existing configuration can be kept.
    """

    def __init__(self, height, width, rotation=0,):
        """

        """
        # Initiate pins

        self._partial_updates_enabled = False
        self._partial_update_count = None
        self._is_initialised = True

        # Cleared when busy pin is logically false (physically 1).
        self._busy = False

        # Initiate the generic display features
        super().__init__(height=height, width=width, rotation=rotation)
        self.clear()

    def clear(self):
        # Clear the display
        upylog.trace('[IcDevice.clear]')
        self.fill(self.palette.WHITE)
        #self.apply_full_update()
        # self.show()


    @property
    def is_initialised(self):
        return self._is_initialised

    def show(self):
        display(buffer_2_pilimg(self, scale=SCALE))


    @property
    def ready(self):
        return not self._busy


    def shutdown(self):
        upylog.info('[IcDevice.shutdown] Display shutting down')
        self.clear()

    def _deep_sleep(self):
        raise NotImplementedError()


class PartialUpdateMixin():#metaclass=ABCMeta):
    _maximum_partial_updates = 60

    #@abstractmethod
    def enable_partial_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        upylog.trace('PartialUpdateMixin.enable_partial_updates')
        if self._partial_updates_enabled:
            upylog.debug('PartialUpdateMixin.enable_partial_updates: Partial updates already enabled.')
            return
        upylog.debug('PartialUpdateMixin.enable_partial_updates: Enabling partial updates already enabled.')
        self._partial_updates_enabled = True
        self._partial_update_count = 0
        self._activate_partial_updates()

    def _activate_partial_updates(self):
        raise NotImplementedError()

    #@abstractmethod
    def enable_full_updates(self):
        """Although not all displays support partial updates, this is exposed to make the interface generic."""
        upylog.trace('PartialUpdateMixin.enable_full_updates')

        if not self._partial_updates_enabled:
            upylog.debug('PartialUpdateMixin.enable_full_updates: Full updates already enabled.')

            return
        upylog.debug('PartialUpdateMixin.enable_full_updates: Enabling full updates.')
        self._partial_updates_enabled = False
        self._activate_full_updates()

    def _activate_full_updates(self):
        raise NotImplementedError()

    def _send_buffer_content(self):
        upylog.trace('PartialUpdateMixin._send_buffer_content')
        if self._partial_updates_enabled:
            upylog.debug((
                'PartialUpdateMixin._send_buffer_content: Sending buffer for partial. '
                'Refresh count: %s / %s . Full refresh requested: %s'),
                self._partial_update_count, self._maximum_partial_updates, self._has_full_updates)

            if ((self._partial_update_count >= self._maximum_partial_updates) or self._has_full_updates):
                upylog.debug('PartialUpdateMixin._send_buffer_content: Temporary full update')
                self.enable_full_updates()
                self._send_buffer_content_full()
                self.enable_partial_updates()
            else:
                self._send_buffer_content_partial()
                self._partial_update_count += 1
        else:
            self._send_buffer_content_full()


class MonoColorDevice(IcDevice):#, metaclass=ABCMeta):
    _palette = palette.PaletteMono()

    @property
    def framebuf_mode(self):
        return framebuf.MONO_HMSB


class TriColorDevice(IcDevice):  #, metaclass=ABCMeta):
    _palette = palette.PaletteTricolor()

    @property
    def framebuf_mode(self):
        return framebuf.GS2_HMSB



class QuadGreyscaleDevice(IcDevice):  # , metaclass=ABCMeta):
    _palette = palette.PaletteGreyscale()

    @property
    def framebuf_mode(self):
        return framebuf.GS2_HMSB
