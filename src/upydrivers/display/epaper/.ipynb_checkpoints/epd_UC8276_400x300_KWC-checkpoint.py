"""
NOTE: This is only compatible with the V1 version of this display.
I haven't yet confirmed, but I think V2, uses controller SSD1683.

This driver is compatible with ePaper screens
using controller UC8276:
- WaveShare 4.2inch epaper (B), Black/White/Red, 400x300 v1
https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(B)_Manual
- WaveShare 4.2inch epaper (C), Black/White/Yellow, 400x300 v1
https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(C)_Manual

Other examples of code that supports this display:
https://github.com/waveshareteam/Pico_ePaper_Code/blob/main/python/Pico-ePaper-4.2-B.py
https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in2bc.py


"""

from upydrivers.display.epaper.icdevice import TriColorDevice


class DisplayDevice(TriColorDevice):
    _name = "epd_UC8276_400x300_KWC"
    _width, _height = 400, 300

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)

    def _send_initialise_configuration_commands(self):
        # 7. Booster Soft Start (BTST)
        #self._send_command(0x06, b"\x17\x17\x17")

        # 2. Power Setting (PWR)
        #self._send_command(0x01, b"\x03\x00\x26\x26\x03")  # Default
        # self._send_command(0x01, b"\x03\x00\x2b\x2b\x09")  # Wav reference doc

        # 5. Power ON (PON)
        self._send_command(0x04)  # POWER ON
        self._sleep_ms(100)
        self._wait_until_ready()

        # 1. PANEL SETTING (PSR)
        # Load the default settings
        self._send_command(0x00, b"\x0F")

        # 33. Resolution setting (TRES)
        # self._send_command(0x61, b"\x03\x20\x01\xE0")  # 800 x 480
        # (WIDTH // 256), (WIDTH % 256), (HEIGHT // 256), (HEIGHT % 256)
        # Default resolution is 800 x 600, # Todo - check this

        # 13. DUAL SPI MODE (DUSPI)
        # self._send_command(0x15, b"\x00")

        # 18. VCOM and data interval setting (CDI)
        self._send_command(0x50, b"\xf7")

        # 32. TCON SETTING (TCON)
        # This command defines non-overlap period of Gate and Source.
        # Default value
        # self._send_command(0x60, b"\x22")

        # 34. GATE/SOURCE START SETTING (GSST)
        # TODO This is in the Pico-ePaper-7.5-B.py driver as "Resolution setting".
        #  I think it's  erroneous and it's the default any way.
        # self._send_command(0x65, b"\x00\x00\x00\x00")

    def _send_refresh_commands(self):
        # TODO verify these! I think I copied these from a BW display
        refresh_commands = [
            (0x04,),  # C5: PON (Power on)
            (0x12,),  # C11: DRF (Display Refresh)
            (0x50, b"\xf7"), # 18: VCOM and data interval setting (CDI)
            (0x02,),  # C3: POF (Power Off)
        ]
        self._send_commands(refresh_commands)

    def _deep_sleep(self):
        raise NotImplementedError()
        self._send_command(b"\x07", b"\xa5")
        self.is_initialised = False

