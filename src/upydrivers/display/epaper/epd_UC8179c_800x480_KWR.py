"""
This driver is compatible with ePaper screens
using controller UC8179c:
 - GooDisplay 7.5inch Black/White/Red 800x480 (GDEY075Z08)
 https://www.good-display.com/product/394.html

Examples of code supporting this display:
https://www.good-display.com/product/394.html

"""


from upydrivers.display.epaper.icdevice import TriColorDevice


class DisplayDevice(TriColorDevice):
    _name = "epd_UC8179c_800x480_KWR"
    _width, _height = 800, 480

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)

    def _send_initialise_configuration_commands(self):
        # 2. Power Setting (PWR)
        # Commented out in the picoEPaper7.5B driver.
        # Including as it's defined in the Display_EPD_W21 Arduino driver
        #  self._send_command(0x01, b"\x07\x07\x3f\x3f")
        # x07: ??? # x07: VGH=20V,VGL=-20V
        # x3f: VDH=15V # x3f: VDL=-15V

        # 7. Booster Soft Start (BTST)
        self._send_command(0x06, b"\x17\x17\x28\x17")
        # x17: 00/010/111 = Default BT_PHA options
        # x17: 00/010/111 = Default BT_PHB options
        # x28: xx/101/000 = BT_PHC1; Raised strength, reduced off time
        # "If an exception is displayed, try using 0x38, default is 17"
        # Strength for BT_PHC1 (phase C) has been increased from 3 to 6. 0x38 takes it to  8
        # x17: 0/x/010/111 = D7=0 disables BT_PHC2

        # 5. Power ON (PON)
        self._send_command(0x04)  # POWER ON
        # After the Power ON command, the driver will be powered ON.
        # This command will turn on booster, controller, regulators,
        # and temperature sensor will be activated for one-time sensing
        # before enabling booster.
        # When all voltages are ready, the BUSY_N signal will return to high.
        self._sleep_ms(100)
        self._wait_until_ready()

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
        # Default resolution is 800 x 600, # Todo - check this

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
        # self._send_command(0x65, b"\x00\x00\x00\x00")

    def _send_refresh_commands(self):
        # TODO verify these! I think I copied these from a BW display
        refresh_commands = [
            (b"\x04",),  # C5: PON (Power on)
            (b"\x12",),  # C11: DRF (Display Refresh)
            (b"\x02",),  # C3: POF (Power Off)
        ]
        self._send_commands(refresh_commands)

    def _deep_sleep(self):
        raise NotImplementedError()
        self._send_command(b"\x07", b"\xa5")
        self.is_initialised = False

