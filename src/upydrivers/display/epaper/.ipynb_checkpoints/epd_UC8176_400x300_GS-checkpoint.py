"""
NOTE: This is only compatible with the v1 version of this display.
For v2, see Controller SSD1683.

This driver is compatible with ePaper screens
using controller UC8176:
 - WaveShare 4.2inch Black/White,4 Grayscale 400x300 v1
   - https://www.waveshare.com/wiki/Pico-ePaper-4.2
   - https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_Manual

Controller UC8176:
https://www.waveshare.com/w/upload/8/88/UC8176.pdf

Other examples of code that supports this display:
https://github.com/waveshareteam/Pico_ePaper_Code/blob/main/python/Pico-ePaper-4.2.py
https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in2.py
https://github.com/peterhinch/micropython-micro-gui/blob/main/drivers/epaper/pico_epaper_42.py
https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42.py
https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42_gs.py
"""



from upydrivers.display.epaper.icdevice import QuadGreyscaleDevice, PartialUpdateMixin


lut_patterns = {
    'full_vcom': b"\x00\x08\x08\x00\x00\x02\x00\x0F\x0F\x00\x00\x01\x00\x08\x08\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'full_ww/bw': b"\x50\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\xA0\x08\x08\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'full_wb': b"\xA0\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x50\x08\x08\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'full_bb': b"\x20\x08\x08\x00\x00\x02\x90\x0F\x0F\x00\x00\x01\x10\x08\x08\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'partial_vcom': b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'partial_ww/bb': b"\x00\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'partial_bw': b"\x80\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    'partial_wb': b"\x40\x19\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
}
lut_map = {
    'full_update': (
        (b"\x20", 'full_vcom'), (b"\x21", 'full_ww/bw'), (b"\x22", 'full_ww/bw'),
        (b"\x23", 'full_wb'), (b"\x24", 'full_bb'),
    ),
    'partial_update': (
        (b"\x20", 'partial_vcom'), (b"\x21", 'partial_ww/bb'), (b"\x22", 'partial_bw'),
        (b"\x23", 'partial_wb'), (b"\x24", 'partial_ww/bb'),
    )
}


class DisplayDevice(PartialUpdateMixin, QuadGreyscaleDevice):
    _name = "epd_UC8176_400x300_GS"
    _width, _height = 400, 300

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)

    def _activate_partial_updates(self):
        self._send_lut(lut_map['partial_update'], lut_patterns)

    def _activate_full_updates(self):
        self._send_lut(lut_map['full_update'], lut_patterns)

    def _send_initialise_configuration_commands(self):
        # 7. Booster Soft Start (BTST)
        self._send_command(b"\x06", b"\x17\x17\x17")

        # 2. Power Setting (PWR)
        self._send_command(b"\x01", b"\x03\x00\x2b\x2b\x09")  # Default
        # self._send_command(0x01, b"\x03\x00\x2b\x2b\x09")  # Wav reference doc

        # 5. Power ON (PON)
        self._send_command(b"\0x04")  # POWER ON
        self._wait_until_ready(100)

        # 1. PANEL SETTING (PSR)
        # Load the default settings
        self._send_command(b"\x00", b"\xbf")

        # 17. PLL Control (PLL)
        self._send_command(b"\x30", b"\x3c") # or \x3a ?

        # 33. Resolution setting (TRES)
        self._send_command(b"\x61", b"\x01\x90\x01\x2C")  # resolution setting

        # 30. VCM_DC Setting (VDCS)
        self._send_command(b"\x82", b"\x12") # or \x12?

        # 22. VCOM and data interval setting (CDI)
        self._send_command(b"\x50", b"\x97") # or \x87?

        # >> # 13. DUAL SPI MODE (DUSPI)
        # >> self._send_command(b"\x15", b"\x00")

        self.enable_full_updates()

    def _send_refresh_commands(self):
        self._send_command(b"\x04",)   # C5: PON (Power on)
        self._wait_until_ready(100)

        self._send_command(b"\x12",)  # C11: DRF (Display Refresh)
        self._wait_until_ready(100)

        self._send_command(b"\x02",)  # C3: POF (Power Off)

    def _deep_sleep(self):
        self._send_command(b"\x07", b"\xa5")
        self.is_initialised = False

