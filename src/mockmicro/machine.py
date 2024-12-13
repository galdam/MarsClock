
class Pin:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        pass

    @property
    def OUT(self):
        return None

    @property
    def PULL_UP(self):
        return None

    @property
    def IN(self):
        return None


class SPI:
    def __init__(self,  *args, **kwargs):
        pass

    def init(self, baudrate):
        pass

    def write(self,  *args, **kwargs):
        pass