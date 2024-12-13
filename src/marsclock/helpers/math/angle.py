# A wrapper for angle values. As many equations are written in degrees but math uses radians,
# this is included to make it easier to swap between them and avoid any ambiguity

import marsclock.helpers.math.mathplus as math
from marsclock.helpers.math import anglehelpers


class Angle:
    """
    An object to wrap the concept of an Angle. Values given in degrees or radians are stored as such
    and only converted when requested. Hours, minutes, and seconds are stored as degrees.
    """
    def __init__(self, deg=None, rad=None, hr=None, mins=None, sec=None, symbol=None, description=None):
        not_none = [v for v in [deg, rad, hr, mins, sec] if v is not None]
        if len(not_none) == 0:
            raise ValueError("No value given")
        if len(not_none) > 1:
            raise ValueError("Provide only one value")
        self._deg = deg
        self._rad = rad
        if hr is not None:
            self._deg = anglehelpers.hr_2_deg(hr)
        if mins is not None:
            self._deg = anglehelpers.mins_2_deg(mins)
        if sec is not None:
            self._deg = anglehelpers.sec_2_deg(sec)

        self._symbol = symbol
        self._description = description

    @property
    def deg(self):
        if self._deg is None:
            self._deg = math.degrees(self._rad)
        return self._deg

    @property
    def rad(self):
        if self._rad is None:
            self._rad = math.radians(self.deg_360)
        return self._rad

    @property
    def hr(self):
        return anglehelpers.deg_2_hr(self.deg)

    @property
    def mins(self):
        return anglehelpers.deg_2_mins(self.deg)

    @property
    def sec(self):
        return anglehelpers.deg_2_sec(self.deg)

    @property
    def deg_180(self):
        return anglehelpers.modulo_degrees_180(self.deg)

    @property
    def deg_360(self):
        return anglehelpers.modulo_degrees_360(self.deg)

    @property
    def rad_tau(self):
        return anglehelpers.modulo_radians_tau(self.rad)

    @property
    def symbol(self):
        return self._symbol

    @property
    def description(self):
        return self._description

    def __str__(self):
        return f"Angle(deg={self.deg:.5f}, rad={self.rad:.5f})"

    def describe(self):
        return ', '.join([
            f"{v:.3f} {k}"
            for v, k in [
                (self.deg, 'd'), (self.rad, 'r'),
                (self.hr, 'h'), (self.mins, 'm'), (self.sec, 's')]])

    def __repr__(self):
        return self.__str__()
