
import marsclock.helpers.math.mathplus as math
from marsclock.astro.ephemeris import Ephemeris


class HeliocentricEarthMars:
    PLANET_RADIUS_SCALE = {'Earth': 0.6, 'Mars': 0.9}

    def __init__(self, position, size, j2k, flip_y=True,):
        self.position = position
        self.size = size
        self.radius = self.size // 2
        self.origin = self.position[0] + self.radius, self.position[1] + self.radius
        self.flip_y = flip_y
        self.j2k = j2k
        self.planet_angles = dict()

    def pos(self, x, y):
        y = self.origin[1] + (-1 * (y - self.origin[1])) if self.flip_y else y
        return int(x), int(y)

    def sun(self):
        return self.pos(self.origin[0], self.origin[1])

    def planet_path(self, planet):
        r = self.PLANET_RADIUS_SCALE[planet]
        x, y = self.pos(self.origin[0], self.origin[1])
        return [
            x, y,
            int(r * self.radius),
            int(r * self.radius), ]

    def planet_angle(self, planet):
        if planet not in self.planet_angles:
            e = Ephemeris(planet, self.j2k)
            self.planet_angles[planet] = e.angle_ecl.rad
        return self.planet_angles[planet]

    def planet_position(self, planet, modifier=None):
        r = self.PLANET_RADIUS_SCALE[planet]
        m = 0 if modifier is None else (math.tau * modifier)
        a = self.planet_angle(planet)-m
        x, y = r * math.cos(a) + self.origin[0], r * math.sin(a) + self.origin[1]
        return self.pos(x, y)
