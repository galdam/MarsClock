#from abc import ABCMeta, abstractmethod

try:
    from machine import Pin, SPI
    import framebuf
    import time
except ImportError:
    from mockmicro.machine import Pin, SPI
    from mockmicro import framebuf
    from mockmicro import time

from upydrivers.display import palette
from upydrivers.display.displaydevice import AbstractUPyDisplayDevice
from upydrivers.display.byteoperations import deinterlace_bytearray, rotate_msb_bytearray
from upydrivers import upylog


def data_iterator(data):
    for d in data:
        yield d


BUF1 = bytearray(1)


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

    def __init__(self, height, width, rotation=0,
                 pin_reset=12, pin_busy=13, pin_cs=9, pin_dc=8,
                 spi_sck=10, spi_mosi=11, spi_miso=28, spi_baudrate=10_000_000):
        """

        """
        # Initiate pins
        self._reset_pin = Pin(pin_reset, Pin.OUT)
        self._busy_pin = Pin(pin_busy, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(pin_cs, Pin.OUT)
        self._dc_pin = Pin(pin_dc, Pin.OUT)
        self._spi = SPI(1, sck=Pin(spi_sck), mosi=Pin(spi_mosi), miso=Pin(spi_miso))
        # UC8179 and UC8176 states up to 20MHz
        # /Pico-ePaper-7.5-B.py uses 4MHz
        # Nano-gui says the datasheet (which?) allows 10MHz
        # Using 10MHz as PH seems to know what he's doing
        self._spi.init(baudrate=spi_baudrate)

        self._partial_updates_enabled = False
        self._partial_update_count = None
        self._is_initialised = False

        # Cleared when busy pin is logically false (physically 1).
        self._busy = False
        self._initialise_configuration()

        # Initiate the generic display features
        super().__init__(height=height, width=width, rotation=rotation)
        self.clear()

    def clear(self):
        # Clear the display
        upylog.trace('IcDevice.clear')
        self.fill(self.palette.WHITE)
        self.apply_full_update()
        self.show()

    def _initialise_configuration(self):
        "Reset hardware and send configurations. Used at startup and after deepsleep"
        upylog.trace('IcDevice._initialise_configuration')
        self._reset()
        self._send_initialise_configuration_commands()
        self.is_initialised = True

    @property
    def is_initialised(self):
        return self._is_initialised

    @is_initialised.setter
    def is_initialised(self, i):
        self._is_initialised = i

    #@abstractmethod
    def _send_initialise_configuration_commands(self):
        "The commands to run on initialisation "
        raise NotImplementedError()

    def show(self):
        upylog.trace('IcDevice.show')
        # Only do an update if something was changed
        if not (self._has_full_updates or self._has_partial_updates):
            upylog.debug('IcDevice.show: No updates')
            return
        upylog.debug('IcDevice.show: Has updates')
        # TODO does the order make sense here?
        if not self.is_initialised:
            self._initialise_configuration()
        self._send_buffer()
        self._send_refresh_commands()

        # Reset the update counter
        self._has_full_updates = False
        self._has_partial_updates = False

    def _send_buffer(self):
        upylog.trace('IcDevice._send_buffer')
        if self._busy:
            raise RuntimeError("Cannot refresh: display is busy.")
        self._busy = True  # Immediate busy flag. Pin goes low much later.
        self._send_buffer_content()
        self._busy = False

    def _send_buffer_content(self):
        self._send_buffer_content_full()

    #@abstractmethod
    def _send_buffer_content_full(self):
        raise NotImplementedError()

    def _send_buffer_content_partial(self):
        # Not abstract as it does not need to be imp
        raise NotImplementedError()

    #@abstractmethod
    def _send_refresh_commands(self):
        # PON
        # DRF
        # POF
        # OPTIONAL: DSLP
        # If deep sleep is used, set is_initialised to False
        raise NotImplementedError()

    # ========= Write Commands to the device ========== # #
    def _send_commands(self, commands_list):
        for command in commands_list:
            self._send_command(*command)

    def _send_command(self, command, data=None, data_modifier=None):
        self._dc_pin(0)
        self._cs_pin(0)
        self._spi.write(command)
        self._cs_pin(1)
        if data is not None:
            self._send_data(data, data_modifier=data_modifier)

    def _send_data(self, data, data_modifier=None):
        if data_modifier is None:
            data_modifier = data_iterator
        self._dc_pin(1)
        for b in data_modifier(data):
            self._cs_pin(0)
            BUF1[0] = b
            self._spi.write(BUF1)
            self._cs_pin(1)

    def _send_lut(self, lut_map, lut_patterns):
        for register_command, pattern_id in lut_map:
            self._send_command(register_command, lut_patterns[pattern_id])

    @property
    def ready(self):
        return not (self._busy or (self._busy_pin() == 0))  # 0 == busy

    def _reset(self):
        """Hardware reset"""
        self.is_initialised = False
        for v in (1, 0, 1):
            self._reset_pin(v)
            time.sleep_ms(20)

    def shutdown(self):
        upylog.info('IcDevice.shutdown: Display shutting down')
        self.clear()
        self._deep_sleep()
        self.is_initialised = False

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

    def _send_buffer_content_full(self):
        upylog.trace('MonoColorDevice._send_buffer_content_full')
        self._send_command(
            b"\x13", self._buffer,
            data_modifier=lambda d: rotate_msb_bytearray(
                d, self.width, self.height, self.rotation))
        # TODO VERIFY if x13 is universal for the black channel

    def _send_buffer_content_partial(self):
        upylog.trace('MonoColorDevice._send_buffer_content_partial')
        self._send_buffer_content_full()


class TriColorDevice(IcDevice):  #, metaclass=ABCMeta):
    _palette = palette.PaletteTricolor()

    @property
    def framebuf_mode(self):
        return framebuf.GS2_HMSB

    def _send_buffer_content_full(self):
        upylog.trace('TriColorDevice._send_buffer_content_full')
        self._send_black_channel()
        self._send_color_channel()

    def _send_buffer_content_partial(self):
        upylog.trace('TriColorDevice._send_buffer_content_partial')
        self._send_black_channel()

    def _send_black_channel(self):
        # TODO VERIFY if x10 is universal for the black channel
        # - Verified for epd_UC8276_400x300_KWR
        self._send_command(
            b"\x10", self._buffer,
            data_modifier=lambda d: rotate_msb_bytearray(
                bytearray(deinterlace_bytearray(d, 0)),
                self.width, self.height, self.rotation))

    def _send_color_channel(self):
        # TODO VERIFY if x13 is universal for the color channel
        # - Verified for epd_UC8276_400x300_KWR
        self._send_command(
            b"\x13", self._buffer,
            data_modifier=lambda d: rotate_msb_bytearray(
               bytearray(deinterlace_bytearray(d, 1)),
               self.width, self.height, self.rotation))


class QuadGreyscaleDevice(IcDevice):  # , metaclass=ABCMeta):
    _palette = palette.PaletteGreyscale()

    @property
    def framebuf_mode(self):
        return framebuf.GS2_HMSB

    def _send_buffer_content_full(self):
        upylog.trace('QuadGreyscaleDevice._send_buffer_content_full')

        self._send_x10_channel()
        self._send_x13_channel()

    def _send_buffer_content_partial(self):
        # Include the partial update option command.
        # This should only be called if the partial mixin is included
        raise NotImplementedError()
        #self._send_black_channel()

    def _send_x10_channel(self):
        self._send_command(
            b"\x10", self._buffer,
            data_modifier=lambda d: rotate_msb_bytearray(
                bytearray(deinterlace_bytearray(d, 0)),
                self.width, self.height, self.rotation))

    def _send_x13_channel(self):
        self._send_command(
            b"\x13", self._buffer,
            data_modifier=lambda d: rotate_msb_bytearray(
                bytearray(deinterlace_bytearray(d, 1)),
                self.width, self.height, self.rotation))