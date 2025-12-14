"""

"""

from upydrivers.display.mock_epaper.mock_icdevice import TriColorDevice


class DisplayDevice(TriColorDevice):
    _name = "mock_400x300_KWC"
    _width, _height = 400, 300

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)
