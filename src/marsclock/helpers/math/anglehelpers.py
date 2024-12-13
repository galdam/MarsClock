import marsclock.helpers.math.mathplus as math


def modulo_degrees_180(deg):
    # Get degrees on a -180 to 180 scale
    if -180 <= deg < 180:
        return deg

    deg_reduced = math.fmod(deg, 360.0)
    if deg_reduced > 180.0:
        deg_reduced -= 360.0
    elif deg_reduced <= -180.0:
        deg_reduced += 360.0
    return deg_reduced


def modulo_degrees_360(deg):
    # Get degrees ona 0 to 360 scale
    return deg if (0 <= deg < 360) else deg % 360


def modulo_radians_tau(rad):
    return rad if 0 <= rad < math.tau else rad % math.tau


def deg_2_hr(deg):
    return deg * (24 / 360)


def hr_2_deg(hr):
    return hr / (24 / 360)


def deg_2_mins(deg):
    return deg * (1440 / 360)


def mins_2_deg(mins):
    return mins / (1440 / 360)


def deg_2_sec(deg):
    return deg * (86400 / 360)


def sec_2_deg(sec):
    return sec / (86400 / 360)
