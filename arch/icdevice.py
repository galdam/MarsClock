from abc import ABC, ABCMeta, abstractmethod

try:
    from machine import Pin, SPI
    import framebuf
    import time
except ImportError:
    from mockmicro.machine import Pin, SPI
    from mockmicro import framebuf
    from mockmicro import time


"""
class FrameBufferAdapter(object):
    def __init__(self):
        super(FrameBufferAdapter, self).__init__()
        framebuf.FrameBuffer.__init__(self)
"""




class MonoColorDevice(IcDevice, framebuf.FrameBuffer, metaclass=ABCMeta):
    def __init__(self, height, width, landscape=True):
        self.palette = PaletteBW
        self.landscape = landscape
        if not landscape:
            raise NotImplementedError()
        self.height = min(height, width) if landscape else max(height, width)
        self.width = max(height, width) if landscape else min(height, width)

        self._buffer = bytearray(self.height * self.width // 8)
        mode = framebuf.MONO_HLSB
        self.partial = False
        # Initiate the IcDeviceInterface and inherit from framebuffer
        super().__init__(self._buffer, self.height, self.width, mode)

    def _send_buffer(self):
        if self._busy:
            raise RuntimeError("Cannot refresh: display is busy.")
        self._busy = True  # Immediate busy flag. Pin goes low much later.
        self._send_command(b"\x13", self._buffer)
        self._busy = False


class Bit2ColorDevice(IcDeviceInterface, framebuf.FrameBuffer):
    def __init__(self, height, width, landscape=True):
        self.palette = PaletteBW
        self.landscape = landscape
        if not landscape:
            raise NotImplementedError()

        self.epd_height = height
        self.epd_width = width
        self.pixel_height = min(height, width) if landscape else max(height, width)
        self.pixel_width = max(height, width) if landscape else min(height, width)

        self._buffer = bytearray(self.pixel_height * self.pixel_width // 8)
        mode = framebuf.MONO_HLSB
        self.partial = False
        # Initiate the IcDeviceInterface and inherit from framebuffer
        super().__init__(self._buffer, self.pixel_height, self.pixel_width, mode)

    def _send_buffer(self):
        if self._busy:
            raise RuntimeError("Cannot refresh: display is busy.")
        self._busy = True  # Immediate busy flag. Pin goes low much later.

        if not self.partial:
            self._send_command(b"\x10", self._buffer)
            self._send_command(b"\x13", self._buffer)
        else:
            self._send_command(b"\x13", self._buffer)


class Wav20344_4in2_BW(MonoColorDevice):
    """
    Driver UC8176
    """
    def __init__(self, rotate=False):
        width = 400
        height = 300

        self.rotate = rotate
        super().__init__(height, width)

    def _send_initialise_configuration_commands(self):
        initialise_commands = [
            (b"\x00", b"\x31" + (0)),  # C1: PSR (Panel Settings)
            (b"\x01", b"\x03\x00\x2b\x2b"),  # C2: PWR (Power Setting)
            #(b"\x01", b"\x07\x07\x3f\x3f"),  # C2: PWR (Power Setting)

            (b"\x06", b"\x17\x17\x17"),  # C7: BTST (Booster Soft Start) < UC8176
            #  (b"\x06", b"\x17\x17\x28\x17"),  # C7: BTST (Booster Soft Start) < UC8179

            (b"\x30", b"\x3c"),  # C13: PLL (PLL Setting)
            (b"\x50", b"\x97"),  # C18: CDI (Vcom and data interval setting)
            (b"\x50", b"\xf7"),  # C18: CDI (Vcom and data interval setting)
            (b"\x61", [   # C21: TRES (Resolution Setting)
                (self.epd_width // 256), (self.epd_width % 256),
                (self.epd_height // 256), (self.epd_height % 256)]),
            (b"\x82", b"\x28"),  # C27: VDCS (VCM_DC Setting)
        ]
        for command in initialise_commands:
            self._send_command(*command)

    def _send_refresh_commands(self):
        refresh_commands = [
            (b"\x04", ),  # C5: PON (Power on)
            (b"\x12", ),  # C11: DRF (Display Refresh)
            (b"\x02", ),  # C3: POF (Power Off)
        ]
        for command in refresh_commands:
            self._send_command(*command)
