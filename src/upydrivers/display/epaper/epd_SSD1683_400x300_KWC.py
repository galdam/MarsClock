"""


"""

from upydrivers.display.epaper.icdevice import TriColorDevice
from upydrivers import upylog

class DisplayDevice(TriColorDevice):
    _name = "epd_SSD1683_400x300_KWC"
    _width, _height = 400, 300

    @property
    def black_channel(self):
        return b'\x24'
    
    @property
    def color_channel(self):
        return b'\x26'


    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)

    def _send_initialise_configuration_commands(self):
        upylog.trace('DisplayDevice._send_initialise_configuration_commands')
        # == STEP 1: POWER ON ==
        # Supply VCI
        # Wait 10ms
        upylog.trace('DisplayDevice.wait1')
        self._wait_until_ready(10)

        # == STEP 2: Set Initial Config ==
        # 0x2F: Status Bit Read 

        # Define SPI interface with MCU

        # HW reset
        # Toggle the reset pin? 

        # 0x12: SW reset 
        self._send_command(b"\x12", )
        # Wait 10ms
        upylog.trace('DisplayDevice.wait2')
        self._wait_until_ready(10)

        # == STEP 3: Send Initialisation Code ==
        # 0x01: Set gate driver output
        # self._send_command(b"\x01", )
        # ((EPD_HEIGHT-1)%256), ((EPD_HEIGHT-1)/256), 0x00

        # Set display RAM size 0x11, 0x44, 0x45

        # 0x11: Data Entry mode setting, set the order that X and Y increment
        # Send: 0x03 # Y increment, X increment | counter updated in X direction
        #self._send_command(b"\x11", b"\x03")

        # 0x44: set Ram-X address start/end position
        # Send: 0x00, self.width//8-1
        #self._send_command(b"\x44", b"\x00\x31")

        # 0x45: set Ram-Y address start/end position
        # Send: 0x00, 0x00, (self.height-1)%256), (self.height-1)//256)
        #self._send_command(b"\x45", b"\x00\x00\x12\x0B")

        # 0x3C: Set panel border # Send: 0x05
        self._send_command(b"\x3C", b"\x05")

        # Display update control
        self._send_command(b"\x21", b"\x00\x00")
        upylog.trace('DisplayDevice.wait3')
        self._wait_until_ready(5)

        # == STEP 4: Load Waveform LUT ==
        # 0x18: Sense temperature by int/ext TS
        # Send: 0x80
        self._send_command(b"\x18", b"\x80")

        # Load waveform LUT from OTP by Command 0x22, 0x20 or by MCU

        # 0x22: Display Update Control 2 - 
        # Send: 0xF7

        # 0x20: Master Activation - Activate Display Update Sequence

        # Wait BUSY Low

        upylog.trace('DisplayDevice.wait4')
        self._wait_until_ready(5)

        # == STEP 5: Write Image and Drive Display Panel ==
        # Write image data in RAM by Command 0x4E, 0x4F, 0x24, 0x26

        # 0x4E: Set RAM X address counter
        # Send: 0x00
        self._send_command(b"\x4E", b"\x00")

        # 0x4F: Set RAM Y address counter
        # Send: 0x00, 0x00)
        self._send_command(b"\x4F", b"\x00\x00")

        # Write Data
        # 0x24
        # 0x26

        # 0x0C: Set softstart setting by Command 0x0C

        # Drive display panel
        # 0x22: Display Update Control 2 - 
        # Send: 0xF7


        # _send_refresh_commands
        # 0x20: Master Activation - Activate Display Update Sequence

        upylog.trace('DisplayDevice.wait5')
        self._wait_until_ready(5)

    def _send_refresh_commands(self):
        self._send_command(b"\x22")
        self._send_command(b"\xF7")
        # 0x20: Master Activation - Activate Display Update Sequence
        self._send_command(b"\x20")

        # 0x10: Deep Sleep mode # 03: Enter Deep Sleep Mode 2
        self._send_command(b"\x10", b"\x03")

        self.is_initialised = False

    def _deep_sleep(self):
        upylog.trace('[DisplayDevice._deep_sleep]')
        raise NotImplementedError()
    
        self._send_command(b"\x07", b"\xa5")
        self.is_initialised = False

