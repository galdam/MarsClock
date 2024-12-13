from math import *

# Expand micropython math to include tau
try:
    __ = tau
except AttributeError as err:
    tau = pi * 2


def cubic_equation(a, c, d):
    # solve the special form of the cubic we need.
    # https://www.johndcook.com/blog/2022/11/02/keplers-equation-python/
    assert(a > 0 and c > 0)
    p = c/a
    q = d/a
    k = sqrt( q**2/4 + p**3/27 )
    return cbrt(-q/2 - k) + cbrt(-q/2 + k)


def cbrt(x):
    # https://stackoverflow.com/questions/28014241/how-to-find-cube-root-using-python
    if 0 <= x:
        return x**(1./3.)
    return -(-x)**(1./3.)


def c_divmod(a, b):
    """C style integer division and modulo"""
    q = int(a / b)
    r = a - (q*b)
    return q, r


def point_on_ellipse(center, radius, angle):
    """Angle in radians"""
    center_x, center_y = center
    x_radius, y_radius = radius
    x = center_x + x_radius * cos(angle)
    y = center_y + y_radius * sin(angle)
    return x, y
