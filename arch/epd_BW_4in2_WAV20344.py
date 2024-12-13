
from machine import Pin, SPI
import framebuf
import time
import asyncio
from drivers.boolpalette import BoolPalette


def asyncio_running():
    try:
        _ = asyncio.current_task()
    except:
        return False
    return True




epd_bw_full_partial = {
    'lut_map': {
        'full_vcom': b"\x00\x08\x08\x00\x00\x02\x00\x0F\x0F\x00\x00\x01\x00\x08\x08\x00\
    \x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00",
        'full_ww': b"\x50\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\xA0\x08\x08\x00\x00\x02\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        'full_bw': b"\x50\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\xA0\x08\x08\x00\x00\x02\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        'full_wb': b"\xA0\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x50\x08\x08\x00\x00\x02\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        'full_bb': b"\x20\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x10\x08\x08\x00\x00\x02\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",

        'partial_vcom': b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00",
        'partial_ww': b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00",
        'partial_bw': b"\x80\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00",
        'partial_wb': b"\x40\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00",
        'partial_bb': b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
    \x00\x00\x00\x00",
    },
    'lut_configs': {
        'full_update': (
            (b"\x20", 'full_vcom'), (b"\x21", 'full_ww'), (b"\x22", 'full_bw'),
            (b"\x23", 'full_wb'), (b"\x24", 'full_bb'),
        ),
        'partial_update': (
            (b"\x20", 'partial_vcom'), (b"\x21", 'partial_ww'), (b"\x22", 'partial_bw'),
            (b"\x23", 'partial_wb'), (b"\x24", 'partial_bb'),
        )
    }
}


epd_grey_lut = {
    'vcom': b"\x00\x0A\x00\x00\x00\x01\x60\x14\x14\x00\x00\x01\x00\x14\x00\x00\x00\x01\
\x00\x13\x0A\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'ww': b"\x40\x0A\x00\x00\x00\x01\x90\x14\x14\x00\x00\x01\x10\x14\x0A\x00\x00\
\x01\xA0\x13\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'bw': b"\x40\x0A\x00\x00\x00\x01\x90\x14\x14\x00\x00\x01\x00\x14\x0A\x00\x00\x01\x99\x0C\
\x01\x03\x04\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'wb': b"\x40\x0A\x00\x00\x00\x01\x90\x14\x14\x00\x00\x01\x00\x14\x0A\x00\x00\
\x01\x99\x0B\x04\x04\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'bb': b"\x80\x0A\x00\x00\x00\x01\x90\x14\x14\x00\x00\x01\x20\x14\x0A\x00\x00\
\x01\x50\x13\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
}

wav20344_bw_configuration = {
    'prepower_commands': [
        (b"\x01", b"\x03\x00\x2b\x2b"),  # C2: Power Setting (PWR)
        (b"\x06", b"\x17\x17\x17"), # C7: Booster Soft Start (BTST)
        (b"\x04", None), # Power on
    ],
    'postpower_commands': [
        (b"\x00", b"\xbf"),  # panel setting
        (b"\x30", b"\x3c"),  # PLL setting
        (b"\x61", b"\x01\x90\x01\x2C"),  # resolution setting
        (b"\x82", b"\x28"),  # vcom_DC setting
        (b"\x50", b"\x97"),  # VCOM AND DATA INTERVAL SETTING
    ],
}
wav20344_gs_configuration = {
    'prepower_commands': [
        (b"\x01", b"\x03\x00\x2b\x2b\x13"),  # POWER SETTING
        # Set "red" pixel voltage to 6.2V
        (b"\x06", b"\x17\x17\x17"),  # boost soft start
        (b"\x04"),  # POWER_ON
    ],
    'postpower_commands':[
        (b"\x00", b"\x3F"),  # panel setting. Works with BF and 3F, not with 1F or 2F. But black border.
    # KW-BF   KWR-AF	BWROTP 0f	BWOTP 1f  PGH was 0xBF
        (b"\x30", b"\x3C"),  # PLL setting
        (b"\x61", b"\x01\x90\x01\x2C"),  # resolution setting
        (b"\x82", b"\x12"),  # vcom_DC setting PGH 0x28 in normal driver
        (b"\x50", b"\x57"),  # VCOM AND DATA INTERVAL SETTING PGH 97 black border 57 white border
        # Greyscale LUT
        (b"\x20", epd_grey_lut['vcom']),
        (b"\x21", epd_grey_lut['ww']),
        (b"\x22", epd_grey_lut['bw']),
        (b"\x23", epd_grey_lut['wb']),
        (b"\x24", epd_grey_lut['bb']),
        (b"\x25", epd_grey_lut['ww']),
]
}


# 97white border 77black border
# VBDF 17|D7 VBDW 97 VBDB 57
# VBDF F7 VBDW 77 VBDB 37  VBDR B7



# Framebuf mapping is pixel 0 is in LS 2 bits
@micropython.viper
def _lmap(dest: ptr8, source: ptr8, pattern: int, length: int):
    d: int = 0  # dest index
    s: int = 0  # Source index
    e: int = 0  # Current output byte (8 pixels of 1 bit)
    t: int = 0  # Current input byte (4 pixels of 2 bits)
    while d < length:  # For each byte of o/p
        e = 0
        # Two sets of 4 pixels
        for _ in range(2):
            t = source[s]
            for _ in range(4):
                e |= (pattern >> (t & 3)) & 1
                t >>= 2
                e <<= 1
            s += 1
        dest[d] = e >> 1
        d += 1




class EPaperDriver(framebuf.FrameBuffer):
    """
    An abstract implementation of an epaper driver,
    designed to match the common features of UC8276 and UC8179
    """
    _CMD_REFRESH = b"\x12"  # 11. Display Refresh (DRF) - 12h

    def __init__(self, reset_pin, busy_pin, cs_pin, dc_pin,
                 width, height, palette, landscape,
                 pre_pwr_cmds, post_pwr_cmds):
        # Initiate pins
        self._reset_pin = Pin(reset_pin, Pin.OUT)
        self._busy_pin = Pin(busy_pin, Pin.IN, Pin.PULL_UP)
        self._cs_pin = Pin(cs_pin, Pin.OUT)
        self._dc_pin = Pin(dc_pin, Pin.OUT)
        self._spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(28))
        self._spi.init(baudrate=10_000_000)  # Datasheet allows 10MHz

        # Set immediately on .show().
        # Cleared when busy pin is logically false (physically 1).
        self._busy = False

        self._setup_buffer(width, height, palette, landscape)
        self._startup_device(pre_pwr_cmds, post_pwr_cmds)


    def _setup_buffer(self, width, height, palette, landscape=True):
        self.palette = palette
        self.ncolors = palette.NCOLORS
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


    def _startup_device(self, pre_pwr_cmds, post_pwr_cmds):
        self.reset()
        for command in pre_pwr_cmds:
            self._send_command(*command)
        self.wait_until_ready()
        for command in post_pwr_cmds:
            self._send_command(*command)
        self.set_full_update()
        self.clear()

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

    @micropython.native
    def _send_buffered_data(self, start, pattern, nbytes):
        _lmap(self.ibuf, self._mvb[start:], pattern, nbytes)  # Invert image data for EPD
        self._dc(1)
        self._cs(0)
        self._spi.write(self.ibuf)
        self._cs(1)

    def _send_framebuffer(self, register, pattern):
        self._send_command(self, register)
        fbidx = 0  # Index into framebuf
        nbytes = len(self.ibuf)  # Bytes to send
        didx = nbytes * 2  # Increment of framebuf index
        nleft = len(self._buf)  # Size of framebuf
        while nleft > 0:
            self._send_buffered_data(fbidx, pattern, nbytes)  # Grey-map, buffer and send nbytes
            fbidx += didx  # Adjust for bytes already sent.
            nleft -= didx  # Could be < 0 if framebuf size not divisible by ibuf size
            nbytes = min(nbytes, nleft)  # but iteration will stop


    def _send_lut(self, lm, lut_map):
        for reg, lut_ix in lm:
            self._send_command(reg, lut_map[lut_ix])

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

    def set_full_update(self):  # Normal full updates
        if not self.full_updates:
            self._send_lut(full_update, lut_full)
            self.full_updates = True

    def set_partial_update(self):  # Partial updates
        if self.full_updates:
            self._send_lut(lut_map, lut_part)
            self.full_updates = False

    def clear(self):
        self.fill(self.palette.WHITE)
        self.show()


    def show(self):
        if self._busy:
            raise RuntimeError("Cannot refresh: display is busy.")
        self._busy = True  # Immediate busy flag. Pin goes low much later.
        for register, pattern in self._buffer_patterns:
            self._send_framebuffer(register, pattern)
        self._busy = False
        self.display_refresh()


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
        # (sum([0 if ncolors == 3 else 32, 0 if rotate180 else 12, 3])
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
        # TODO Verify this command
        self._send_command(0x65, b"\x00\x00\x00\x00")


