"""

"""

from upydrivers.display.mock_epaper.mock_icdevice import MonoColorDevice


class DisplayDevice(MonoColorDevice):
    _name = "mock_400x300_KW"
    _width, _height = 400, 300

    def __init__(self, rotation=0, **kwargs):
        super().__init__(height=self._height, width=self._width,
                         rotation=rotation, **kwargs)
