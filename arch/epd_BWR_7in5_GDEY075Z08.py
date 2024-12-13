
import framebuf
import time
import asyncio
from drivers.boolpalette import BoolPalette


# I think command 35can be used to check the chip version



# Number of colors: 2 or 3:
# - definition of the frame buffer
# - setup
# - data writing command






class PaletteBWR:
    WHITE = 3 # 0b11
    RED = 2  # 0b10
    BLACK = 1 # 0b01


class PaletteBW:
    WHITE = 1
    BLACK = 0

class PaletteGS:
    WHITE = 3
    DARK_GRAY = 2
    LIGHT_GRAY = 1
    BLACK = 0



class EpdFrameBuffer(framebuf.FrameBuffer):
    def __init__(self, height, width, ncolors, landscape=True):
        self.ncolors = ncolors
        self.orient_landscape = landscape
        self.height = height if landscape else width
        self.width = width if landscape else height
        if self.ncolors == 2:
            self._buffer = bytearray(self.height * self.width // 8)
            mode = framebuf.MONO_VLSB if landscape else framebuf.MONO_HLSB
        elif self.ncolors <= 4:
            self._buffer = bytearray(self.height * self.width // 4)
            mode = framebuf.GS2_VLSB if landscape else framebuf.GS2_HLSB
        else:
            raise NotImplementedError("Support not enabled for more than 4 colors")

        super().__init__(self._buffer, self.height, self.width, mode)




class EPaperDriver():
    """
    An abstract implementation of an epaper driver,
    designed to match the common features of UC8276 and UC8179
    """
    _CMD_REFRESH = b"\x12"  # 11. Display Refresh (DRF) - 12h

    def __init__(self, reset_pin, busy_pin, cs_pin, dc_pin, width, height):
        # Initiate pins
        self._reset_pin = Pin(reset_pin, Pin.OUT)
        self._busy_pin = Pin(busy_pin, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(cs_pin, Pin.OUT)
        self._dc_pin = Pin(dc_pin, Pin.OUT)
        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(28))
        # Datasheet allows 10MHz
        # UC8179 and UC8176 states up to 20MHz
        # /Pico-ePaper-7.5-B.py uses 4MHz
        self._spi.init(baudrate=10_000_000)

        # Set immediately on .show().
        # Cleared when busy pin is logically false (physically 1).
        self._busy = False

        self.width = width
        self.height = height


    # ========= Write Commands to the device ========== # #

    def _send_command(self, command, data=None):
        self._dc_pin(0)
        self._cs_pin(0)
        self._spi.write(command)
        self._cs_pin(1)
        if data is not None:
            self._send_data(data)

    def _send_data(self, data, buf1=bytearray(1)):
        self._dc_pin(1)
        for b in data:
            self._cs_pin(0)
            buf1[0] = b
            self._spi.write(buf1)
            self._cs_pin(1)

    @property
    def ready(self):
        return not (self._busy or (self._busy_pin() == 0))  # 0 == busy

    def wait_until_ready(self):
        while not self.ready:
            time.sleep_ms(100)

    def reset(self):
        """Hardware reset"""
        for v in (1, 0, 1):
            self._reset_pin(v)
            time.sleep_ms(20)

    def display_refresh(self):
        self._send_command(self._CMD_REFRESH)  # Display Refresh (DRF) - 12h
        time.sleep_ms(100)
        self.wait_until_ready()

    def clear(self):
        self.fill(CW)
        self.show()






class IcUc8179:
    def __init__(self, reset_pin=None, ):
        pass
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





class EPD(framebuf.FrameBuffer):
    # Display resolution
    _EPD_WIDTH = const(800)
    _EPD_HEIGHT = const(480)
    _BWIDTH = _EPD_WIDTH // 4  # FB width in bytes (2 bits/pixel)


    # Discard asyn arg: autodetect
    def __init__(self):
        # Initiate pins
        self._reset_pin = Pin(_RESET_PIN, Pin.OUT)
        self._busy_pin = Pin(_BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(_CS_PIN, Pin.OUT)
        self._dc_pin = Pin(_DC_PIN, Pin.OUT)
        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(28))
        self._spi.init(baudrate=10_000_000)  # Datasheet allows 10MHz
        self._busy = False  # Set immediately on .show(). Cleared when busy pin is logically false (physically 1).

        # Async API
        self.updated = asyncio.Event()
        self.complete = asyncio.Event()

        self.width = self._EPD_WIDTH
        self.height = self._EPD_HEIGHT

        self._buf = bytearray(self._EPD_HEIGHT * self._BWIDTH)
        self._mvb = memoryview(self._buf)
        self.ibuf = bytearray(1000)  # Buffer for mapped pixels
        # Patterns for the two hardware buffers.
        # LS 4 bits are o/p colors for white, grey1, grey2, black
        self._patterns = (0b0011, 0b0101)
        mode = framebuf.GS2_HMSB
        self.palette = BoolPalette(mode)
        super().__init__(self._buf, _EPD_WIDTH, _EPD_HEIGHT, mode)
        self.init()
        time.sleep_ms(500)


    def startup(self):
        # EPD hardware init start
        self.reset()

        # 2. Power Setting (PWR)
        # Commented out in the picoEPaper7.5B driver.
        # Including as it's defined in the Display_EPD_W21 Arduino driver
        self._send_command(0x01, b"\x07\x07\x3f\x3f")
        #         self.send_command(0x01)  # POWER SETTING
        #         self.send_data(0x07)
        #         self.send_data(0x07)     # VGH=20V,VGL=-20V
        #         self.send_data(0x3f)     # VDH=15V
        #         self.send_data(0x3f)     # VDL=-15V

        # 7. Booster Soft Start (BTST)
        self._send_command(0x06, b"\x17\x17\x28\x17")
        # x17: 00/010/111
        # x17: 00/010/111
        # x28: xx/101/000   # If an exception is displayed, try using 0x38, default is 17
        # Strength for BT_PHC1 (phase C) has been increased from 3 to 6. 0x38 takes it to  8
        # x17: 0/x/010/111

        # 5. Power ON (PON)
        # Todo Should power on be called _after_ the above?
        self.send_command(0x04)  # POWER ON
        # After the Power ON command, the driver will be powered ON.
        # Refer to the POWER MANAGEMENT section for the sequence.
        # This command will turn on booster, controller, regulators,
        # and temperature sensor will be activated for one-time sensing
        # before enabling booster.
        # When all voltages are ready, the BUSY_N signal will return to high.
        self.delay_ms(100)

        self.wait_until_ready()

        # 1.Panel Setting (PSR). Default 0x0F
        # TODO Try setting UD to 0 and scanning up to flip the screen?
        self._send_command(0x00, b"\x0f")
        # D5 REG; *0: LUT from OTP / 1: LUT from register
        # D4 KW/R; *0: Black, white, red mode / 1: Black, white mode
        # D3 UD; 0: Scan down / *1: Scan up
        # D2 SHL; 0: Source Shift Direction left / *1: shift right
        # D1 SHD_N; 0: Booster switch off / *1: on
        #      When SHD_N becomes LOW, charge pump will be turned OFF,
        #      register and SRAM data will keep until VDD OFF.
        #      And Source/Gate/Border/VCOM will be released to floating.
        # D0 RST_N; 0: Reset Booster Off / *1: No effect
        #      Register data are set to their default values,
        #      all drivers will be reset, and all functions will be disabled.
        #      Source/Gate/Border/VCOM will be released to floating.

        # 33. Resolution setting (TRES)
        self._send_command(0x61, b"\x03\x20\x01\xE0")  # 800 x 480
        # (WIDTH // 256), (WIDTH % 256), (HEIGHT // 256), (HEIGHT % 256)
        # Default resolution is 800 x 600,

        # 13. DUAL SPI MODE (DUSPI)
        self._send_command(0x15, b"\x00")

        # 29. VCOM and data interval setting (CDI)
        self._send_command(0x50, b"\x11\x07")  # VCOM AND DATA INTERVAL SETTING
        # 0001|0001
        # BDZ: 0 0: Border output Hi-Z disabled (default)
        # BDV: 01 LUTW: Border LUT selection
        # N2OCP:0 Copy frame data from NEW data to OLD data enable control
        #          after display refresh with NEW/OLD in KW mode.
        #          Copy NEW data to OLD data disabled (default)
        # DDX:01: default
        # CDI: x07: 10 (Default)

        # 32. TCON SETTING (TCON)
        # This command defines non-overlap period of Gate and Source.
        # Default value
        self._send_command(0x60, b"\x22")

        # 34. GATE/SOURCE START SETTING (GSST)
        # TODO This is in the Pico-ePaper-7.5-B.py driver as "Resolution setting".
        #  I think it's  erroneous and it's the default any way.
        #self._send_command(0x65, b"\x00\x00\x00\x00")

