
import marsclock.helpers.math.mathplus as math
from marsclock.helpers.math.angle import Angle, anglehelpers

DAY_SECONDS = 60 * 60 * 24
SIDEREAL_RATE = 1.00273790935


def sidereal_2_clock(sidereal_angle):
    return (DAY_SECONDS * sidereal_angle.deg / SIDEREAL_RATE) / 360


def ecliptic_2_equatorial(x_ecl, y_ecl, z_ecl, epsilon):
    """
    Transform from ecliptic coordinates to equatorial.
    Rotating by epsilon, the obliquity of the observer
    """
    x_eq = x_ecl
    y_eq = math.cos(epsilon.rad) * y_ecl - math.sin(epsilon.rad) * z_ecl
    z_eq = math.sin(epsilon.rad) * y_ecl + math.cos(epsilon.rad) * z_ecl
    return x_eq, y_eq, z_eq


def rectangular_2_spherical(x, y, z):
    """
    Convert from rectangular coordinates (x, y, z)
    to spherical (r: radius, ra: right ascension, dec: declination)
    """
    r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    ra = Angle(rad=math.atan2(y, x) % (2 * math.pi))
    dec = Angle(rad=math.asin(z / r))
    return r, ra, dec
