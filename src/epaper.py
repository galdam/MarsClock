# pico_epaper_42.py A 1-bit monochrome display driver for the Waveshare Pico
# ePaper 4.2" display. This version fixes bugs and supports partial updates.
# https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42.py

# Adapted from the Waveshare driver by Peter Hinch Sept 2022-May 2023.
# https://www.waveshare.com/pico-epaper-4.2.htm
# UC8176 manual https://www.waveshare.com/w/upload/8/88/UC8176.pdf
# Waveshare's copy of this driver.
# https://github.com/waveshare/Pico_ePaper_Code/blob/main/pythonNanoGui/drivers/ePaper4in2.py
# https://github.com/waveshare/Pico_ePaper_Code/blob/main/python/Pico-ePaper-4.2.py

# *****************************************************************************
# * | File        :	  Pico_ePaper-3.7.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-06-01
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# If .set_partial() is called, subsequent updates will be partial. To restore normal
# updates, issue .set_full()

from machine import Pin, SPI
import framebuf
import time
import asyncio
#from drivers.boolpalette import BoolPalette


CK = 0
CW = 1

"""
class BoolPalette(framebuf.FrameBuffer):
    def __init__(self, mode):
        buf = bytearray(4)  # OK for <= 16 bit color
        super().__init__(buf, 2, 1, mode)

    def fg(self, color):  # Set foreground color
        self.pixel(1, 0, color)

    def bg(self, color):
        self.pixel(0, 0, color)



def asyncio_running():
    try:
        _ = asyncio.current_task()
    except:
        return False
    return True
"""

# Display resolution
_EPD_WIDTH = const(400)
_EPD_HEIGHT = const(300)
_BWIDTH = _EPD_WIDTH // 8

_RESET_PIN = const(12)  # Rear socket pinout
_DC_PIN = const(8)
_CS_PIN = const(9)
_BUSY_PIN = const(13)

# LUT elements vcom, ww, bw, wb, bb
# ****************************** full screen update LUT********************************* #

lut_full = (b"\x00\x08\x08\x00\x00\x02\x00\x0F\x0F\x00\x00\x01\x00\x08\x08\x00\
\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00",
    b"\x50\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\xA0\x08\x08\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    b"\x50\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\xA0\x08\x08\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    b"\xA0\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x50\x08\x08\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    b"\x20\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x10\x08\x08\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
)

# ******************************partial screen update LUT********************************* #

lut_part = (
    b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00",
    b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00",
    b"\x80\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00",
    b"\x40\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00",
    b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00",
)

# [index into LUT, register address]. Design allows for repeats as per greyscale driver.
lut_map = ((0, b"\x20"), (1, b"\x21"), (2, b"\x22"), (3, b"\x23"), (4, b"\x24"))

"""
# Invert: EPD is black on white
# 337/141 us for 2000 bytes (125/250MHz)
@micropython.viper
def _linv(dest: ptr32, source: ptr32, length: int):
    n: int = length - 1
    z: uint32 = int(0xFFFFFFFF)
    while n >= 0:
        dest[n] = source[n] ^ z
        n -= 1
"""

# Bit reverse an 8 bit value
def rbit8(v):
    v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
    v = (v & 0x33) << 2 | (v & 0xcc) >> 2
    return (v & 0x55) << 1 | (v & 0xaa) >> 1


class EPD(framebuf.FrameBuffer):
    # A monochrome approach should be used for coding this. The rgb method ensures
    # nothing breaks if users specify colors.
    """
    @staticmethod
    def rgb(r, g, b):
        return int((r > 127) or (g > 127) or (b > 127))
    """

    def __init__(self, rotate=True):
        self.width = _EPD_WIDTH
        self.height = _EPD_HEIGHT
        self.rotate = rotate
        self.full_updates = None

        self._reset_pin = Pin(_RESET_PIN, Pin.OUT)
        self._busy_pin = Pin(_BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(_CS_PIN, Pin.OUT)
        self._dc_pin = Pin(_DC_PIN, Pin.OUT)
        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(28))
        #self._spi._setup(baudrate=10_000_000)  # Datasheet limit 10MHz

        # Busy flag: set immediately on .show().
        # Cleared when busy pin is logically false.
        self._busy = False

        # Async API
        self.updated = asyncio.Event()
        self.complete = asyncio.Event()

        # Buffer
        self._buf = bytearray(_EPD_HEIGHT * _BWIDTH)
        self._mvb = memoryview(self._buf)
        self._ibuf = bytearray(1000)  # Buffer for inverted pixels

        mode = framebuf.MONO_HLSB
        # self.palette = BoolPalette(mode)  # Enable CWriter.
        super().__init__(self._buf, _EPD_WIDTH, _EPD_HEIGHT, mode)
        self._setup()
        time.sleep_ms(500)

    def _setup(self):
        self.reset()

        self._send_command(b"\x01", b"\x03\x00\x2b\x2b")  # C2: Power Setting (PWR)
        self._send_command(b"\x06", b"\x17\x17\x17")  # C7: Booster Soft Start (BTST)
        self._send_command(b"\x04")  # Power on

        self.wait_until_ready()

        self._send_command(b"\x00", b"\xbf")  # panel setting
        self._send_command(b"\x30", b"\x3c")  #  PLL setting
        self._send_command(b"\x61", b"\x01\x90\x01\x2C")  # resolution setting
        self._send_command(b"\x82", b"\x28")  # vcom_DC setting
        self._send_command(b"\x50", b"\x97")  # VCOM AND DATA INTERVAL SETTING
        # 97white border 77black border
        # VBDF 17|D7 VBDW 97 VBDB 57
        # VBDF F7 VBDW 77 VBDB 37  VBDR B7

        self.set_full_update()
        self.clear()

    # ========= Write Commands to the device ========== # #

    def _send_command(self, command, data=None, reverse=False):
        self._dc_pin(0)
        self._cs_pin(0)
        self._spi.write(command)
        self._cs_pin(1)
        if data is not None:
            self._send_data(data, reverse=reverse)

    # Datasheet P26 seems to mandate CS False after each byte. Ugh.
    def _send_data(self, data, buf1=bytearray(1), reverse=False):
        self._dc_pin(1)
        for b in (reversed(data) if reverse else data):
            self._cs_pin(0)
            buf1[0] = rbit8(b) if reverse else b
            self._spi.write(buf1)
            self._cs_pin(1)

    """
    @micropython.native
    def _send_buffered(self, start, nbytes, reverse=False):
        # Invert b<->w, buffer and send nbytes source bytes
        # Invert and buffer is done 32 bits at a time, hence >> 2
        _linv(self._ibuf, self._mvb[start:], nbytes >> 2)
        self._dc(1)
        self._cs(0)
        if reverse:
            self._spi.write(map(rbit8, reversed(self._ibuf)))
        else:
            self._spi.write(self._ibuf)
        self._cs(1)
    """

    def _send_lut(self, lm, lut):
        for idx, reg in lm:
            self._send_command(reg, lut[idx])

    @property
    def ready(self):
        # 0 == busy. Comment in official code is wrong. Code is correct.
        return not (self._busy or (self._busy_pin() == 0))  # 0 == busy

    def wait_until_ready(self):
        while not self.ready:
            time.sleep_ms(100)

    # ======= Commands from the user ======== #

    def set_full_update(self):  # Normal full updates
        if not self.full_updates:
            self._send_lut(lut_map, lut_full)
            self.full_updates = True

    def set_partial_update(self):  # Partial updates
        if self.full_updates:
            self._send_lut(lut_map, lut_part)
            self.full_updates = False

    def reset(self):
        """Hardware reset"""
        for v in (1, 0, 1):
            self._reset_pin(v)
            time.sleep_ms(20)

    def display_refresh(self):
        self._send_command(b"\x12")
        time.sleep_ms(100)
        self.wait_until_ready()

    def clear(self):
        self.fill(CW)
        self.show()

    def text(self, s, x, y, c=None, bg=None):
        "If a background color is used, draw a background box first"
        if bg is not None:
            self.rect(x, y, 8 * len(s), 8, bg, True)
        super().text(s, x, y, c)

    """
    # Time to convert and transmit 1000 bytes ~ 1ms: most of that is tx @ 10MHz
    # Yield every 16 transfers means blocking is ~16ms
    # Total convert and transmit time for 15000 bytes is ~15ms.
    # Timing @10MHz/250MHz: full refresh 2.1s, partial 740ms: the bulk of the time
    # is spent spinning on the busy pin and is CPU frequency independent.
    async def _as_show(self):
        self._send_command(b"\x13")
        fbidx = 0  # Index into framebuf
        nbytes = len(self._ibuf)  # Bytes to send
        nleft = len(self._buf)  # Size of framebuf
        npass = 0
        while nleft > 0:
            self._send_buffered(fbidx, nbytes)  # Invert, buffer and send nbytes
            fbidx += nbytes  # Adjust for bytes already sent
            nleft -= nbytes
            nbytes = min(nbytes, nleft)
            if not ((npass := npass + 1) % 16):
                await asyncio.sleep_ms(0)  # Control blocking time
        self.updated.set()
        self._send_command(b"\x12")  # Nonblocking .display_on()
        while not self._busy_pin():  # Wait on display hardware
            await asyncio.sleep_ms(0)
        self._busy = False
        self.complete.set()

    # Specific method for micro-gui. Unsuitable EPD's lack this method. Micro-gui
    # does not test for asyncio as this is guaranteed to be up.
    async def do_refresh(self, split):
        assert not self._busy, "Refresh while busy"
        await self._as_show()  # split=5
    """

    def show(self):
        if self._busy:
            raise RuntimeError("Cannot refresh: display is busy.")
        self._busy = True  # Immediate busy flag. Pin goes low much later.
        self._send_command(b"\x13", self._buf, reverse=self.rotate)
        """
        fbidx = 0  # Index into framebuf
        nbytes = len(self._ibuf)  # Bytes to send
        nleft = len(self._buf)  # Size of framebuf
        while nleft > 0:
            self._bsend(fbidx, nbytes)  # Invert, buffer and send nbytes
            fbidx += nbytes  # Adjust for bytes already sent
            nleft -= nbytes
            nbytes = min(nbytes, nleft)
        """
        self._busy = False
        self.display_refresh()


    def sleep(self):
        self._send_command(b"\x50", b"\xf7") # Vcom and data interval setting (CDI)
        # VCOM AND DATA INTERVAL SETTING PGH 97 black border 57 white border
        # border floating? '11110111'
        self._send_command(b"\x02")  # C4: Power OFF Sequence Setting (PFS)
        self.wait_until_ready()
        # Todo: ^^ check if we need the stuff above ^^
        self._send_command(b"\x07", b"\xa5")  # deep sleep



if __name__ == '__main__':
    epd = EPD()
    
    """print('Write message one to buffer')
    epd.text("Waveshare", 5, 10, CK)
    epd.text("Pico_ePaper-4.2-B", 5, 40, CW)
    epd.text("Raspberry Pico", 5, 70, CK)
    print('Display message one')
    epd.show()
    time.sleep(2)"""
    epd.fill(CW)
    epd.text("Waveshare", 15, 10, CK)
    epd.text("Pico_ePaper-4.2-B", 15, 40, CK)
    epd.text("Raspberry Pico", 15, 70, CK)
    epd.show()
    time.sleep(2)
    
    epd.set_partial_update()
    for i in range(10):
        print(i)
        msg = f"Num: {i}"
        #epd.rect(20, 80, 8*len(msg), 8, 0, True)
        epd.text(msg, 20, 80, CK, CW)
        epd.show()
        time.sleep(1)
    
    epd.set_full_update()
    epd.text("Raspberry Pico", 15, 100, 3)
    epd.show()
    time.sleep(2)
    
    print("Clear screen")
    epd.clear()
    print("Shutting down")
    epd.sleep()
    print("~ DONE ~")