from machine import Pin, SPI
import framebuf
import time

_EPD_WIDTH = 400
_EPD_HEIGHT = 300

_RESET_PIN = 12  # Rear socket pinout
_DC_PIN = 8
_CS_PIN = 9
_BUSY_PIN = 13


# Color mapping.
# There is no LUT - colors.py creates 13 color constants which have 2-bit values determined
# by EPD.rgb(). These 2-bit values are written to the framebuf. The _lmap function produces
# 1-bit colors which are written to two buffers on the hardware. Each buffer is written using
# a different LUT so that grey values appear as 1 in one hardware buffer and 0 in the other.


# Framebuf mapping is pixel 0 is in LS 2 bits
@micropython.viper
def _lmap(dest: ptr8, source: ptr8, pattern: int, length: int):
    d: int = 0  # dest index
    s: int = 0  # Source index
    e: int = 0  # Current output byte (8 pixels of 1 bit
    t: int = 0  # Current input byte (4 pixels of 2 bits)
    while d < length:  # For each byte of o/p
        e = 0
        # Two sets of 4 pixels
        for _ in range(2):
            t = source[s]
            for _ in range(4):
                e |= ((pattern >> (t & 3)) & 1)
                t >>= 2
                e <<= 1
            s += 1

        dest[d] = e >> 1
        d += 1


class BoolPalette(framebuf.FrameBuffer):
    def __init__(self, mode):
        buf = bytearray(4)  # OK for <= 16 bit color
        super().__init__(buf, 2, 1, mode)

    def fg(self, color):  # Set foreground color
        self.pixel(1, 0, color)

    def bg(self, color):
        self.pixel(0, 0, color)

# Bit reverse an 8 bit value
def rbit8(v):
    v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
    v = (v & 0x33) << 2 | (v & 0xcc) >> 2
    return (v & 0x55) << 1 | (v & 0xaa) >> 1


class AbstractEPD(framebuf.FrameBuffer):
    @staticmethod
    def rgb(r, g, b):
        return min((r + g + b) >> 7, 3)  # Greyscale in range 0 <= gs <= 3

    def __init__(self, asyn=False):
        self.width = _EPD_WIDTH
        self.height = _EPD_HEIGHT
        self._busy = False  # Set immediately on .show(). Cleared when busy pin is logically false (physically 1).

        # Setup pins
        self._reset_pin = Pin(_RESET_PIN, Pin.OUT)
        self._busy_pin = Pin(_BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(_CS_PIN, Pin.OUT)
        self._dc_pin = Pin(_DC_PIN, Pin.OUT)
        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(28))

         # Async API
        self.updated = asyncio.Event()
        self.complete = asyncio.Event()

        self._byte_array, mode, self.patterns = self.__setup_buffer()

        self._mvb = memoryview(self._byte_array)
        self.ibuf = bytearray(1000)  # Buffer for mapped pixels
        # Patterns for the two hardware buffers.

        self.palette = BoolPalette(mode)
        super().__init__(self._byte_array, _EPD_WIDTH, _EPD_HEIGHT, mode)
        self.init()
        time.sleep_ms(500)


    def __setup_buffer(self):
        _byte_array = bytearray(_EPD_HEIGHT * _EPD_WIDTH // 4)
        mode = framebuf.GS2_HMSB
        # LS 4 bits are o/p colors for white, grey1, grey2, black
        _patterns = (0b0011, 0b0101)

        return _byte_array, mode, _patterns

    def reset(self):
        """Hardware reset"""
        for v in (1, 0, 1):
            self._reset_pin(v)
            time.sleep_ms(20)

    def _send_command(self, command, data=None, reverse=False):
        self._dc_pin(0)
        self._cs_pin(0)
        self._spi.write(command)
        self._cs_pin(1)
        if data is not None:
            self._send_data(data, reverse=reverse)


    def _send_data(self, data, buf1=bytearray(1), reverse=False):
        self._dc_pin(1)
        for b in (reversed(data) if reverse else data):
            self._cs_pin(0)
            buf1[0] = rbit8(b) if reverse else b
            self._spi.write(buf1)
            self._cs_pin(1)


    @micropython.native
    def _bsend(self, start, pattern, nbytes):
        buf = self.ibuf
        _lmap(buf, self._mvb[start:], pattern, nbytes)  # Invert image data for EPD
        self._dc_pin(1)  # << Not 0 like in send data?
        self._cs_pin(0)
        self._spi.write(buf)
        self._cs_pin(1)

    def set_partial(self):  # Allow demos to run
        pass

    def set_full(self):
        pass