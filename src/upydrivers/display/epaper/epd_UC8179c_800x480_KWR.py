"""
This driver is compatible with ePaper screens
using controller UC8179c:
 - GooDisplay 7.5inch Black/White/Red 800x480 (GDEY075Z08)
 https://www.good-display.com/product/394.html

Examples of code supporting this display:
https://www.good-display.com/product/394.html

"""

from upydrivers.display.epaper.icdevice import TriColorDevice, PartialUpdateMixin
from upydrivers import upylog


class DisplayDevice(PartialUpdateMixin, TriColorDevice):
    _name = "epd_UC8179c_800x480_KWR"
    _width, _height = 800, 480

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)
        
    def _activate_partial_updates(self):
        upylog.trace('DisplayDevice._activate_partial_updates')
        #self._send_lut(lut_map['partial_update'], lut_patterns)

    def _activate_full_updates(self):
        upylog.trace('DisplayDevice._activate_full_updates')
        #self._send_lut(lut_map['full_update'], lut_patterns)

    def _send_initialise_configuration_commands(self):
        # 2. Power Setting (PWR)
        # Commented out in the picoEPaper7.5B driver.
        # Including as it's defined in the Display_EPD_W21 Arduino driver
        self._send_command(b"\x01", b"\x07\x07\x3f\x3f")
        # x07: ??? # x07: VGH=20V,VGL=-20V
        # x3f: VDH=15V # x3f: VDL=-15V

        # 5. Power ON (PON)
        self._send_command(b'\x04')  # POWER ON
        self._wait_until_ready(100)
        # After the Power ON command, the driver will be powered ON.
        # This command will turn on booster, controller, regulators,
        # and temperature sensor will be activated for one-time sensing
        # before enabling booster.
        # When all voltages are ready, the BUSY_N signal will return to high.

        # 1.Panel Setting (PSR). Default 0x0F
        self._send_command(b'\x00', b"\x0f")
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


        # 7. Booster Soft Start (BTST)
        self._send_command(b'\x06', b"\x17\x17\x28\x17")
        # x17: 00/010/111 = Default BT_PHA options
        # x17: 00/010/111 = Default BT_PHB options
        # x28: xx/101/000 = BT_PHC1; Raised strength, reduced off time
        # "If an exception is displayed, try using 0x38, default is 17"
        # Strength for BT_PHC1 (phase C) has been increased from 3 to 6. 0x38 takes it to  8
        # x17: 0/x/010/111 = D7=0 disables BT_PHC2


        # 33. Resolution setting (TRES)
        self._send_command(b'\x61', b"\x03\x20\x01\xE0")  # 800 x 480
        # (WIDTH // 256), (WIDTH % 256), (HEIGHT // 256), (HEIGHT % 256)

        # 13. DUAL SPI MODE (DUSPI)
        self._send_command(b'\x15', b"\x00")

        # 29. VCOM and data interval setting (CDI)
        self._send_command(b'\x50', b"\x11\x07")  # VCOM AND DATA INTERVAL SETTING
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
        self._send_command(b'\x60', b"\x22")

        # 34. GATE/SOURCE START SETTING (GSST)
        # TODO This is in the Pico-ePaper-7.5-B.py driver as "Resolution setting".
        #  I think it's  erroneous and it's the default any way.
        # self._send_command(b'\x65', b"\x00\x00\x00\x00")

    def _send_refresh_commands(self):
        # TODO verify these! I think I copied these from a BW display
        
        upylog.trace('[DisplayDevice._send_refresh_commands]')
        self._send_command(b"\x04",)   # C5: PON (Power on)
        self._wait_until_ready(100)

        self._send_command(b"\x12",)  # C11: DRF (Display Refresh)
        self._wait_until_ready(100)

        #self._send_command(b"\x50", b"\xf7") # Vcom and data interval setting (CDI)
        self._send_command(b"\x02",)  # C3: POF (Power Off)
        self.is_initialised = False

    def _deep_sleep(self):
        self.is_initialised = False
        raise NotImplementedError()
    
        self._send_command(b"\x07", b"\xa5")

