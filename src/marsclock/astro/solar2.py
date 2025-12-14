import marsclock.helpers.math.mathplus as math
from marsclock.astro.ephemeris import Ephemeris


class AbsSolar:
    def __init__(self, position, size, j2k, flip_y=True,):
        self.position = position
        self.size = size
        self.j2k = j2k
        self.flip_y = flip_y
        self.radius = self.size // 2
        self.origin = self.position[0] + self.radius, self.position[1] + self.radius
        self.planet_angles = dict()


class AbsHeliocentric(AbsSolar):
    def __init__(self, position, size, j2k, flip_y=True):
        super().__init__(position, size, j2k, flip_y)

    @property
    def planet_radius_scale(self):
        raise NotImplementedError()

    def planet_angle(self, planet):
        if planet not in self.planet_angles:
            e = Ephemeris(planet, self.j2k)
            self.planet_angles[planet] = e.angle_ecl.rad
        return self.planet_angles[planet]

    def pos(self, x, y):
        y = self.origin[1] + (-1 * (y - self.origin[1])) if self.flip_y else y
        return int(x), int(y)

    def sun(self):
        return self.pos(self.origin[0], self.origin[1])

    def planet_path(self, planet):
        r = int(self.planet_radius_scale[planet] * self.radius)
        x, y = self.pos(self.origin[0], self.origin[1])
        return [x, y, r, r ]

    def planet_position(self, planet, modifier=None):
        r = self.planet_radius_scale[planet]
        m = 0 if modifier is None else (math.tau * modifier)
        a = self.planet_angle(planet)-m
        x, y = r * math.cos(a) + self.origin[0], r * math.sin(a) + self.origin[1]
        return self.pos(x, y)


class HeliocentricEarthMars(AbsHeliocentric):
    def __init__(self, position, size, j2k):
        super().__init__(position, size, j2k)

    @property
    def planet_radius_scale(self):
        return {'Earth': 0.6, 'Mars': 0.9}





class Geocentric:
    

    zodiac = ['Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

    planets = ['Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
    j2k = h.rtc.earth_time.j2kdelta
    planet_angles = []
    for planet in planets:
        e = EphemerisRelative('Earth', j2k, planet)
        planet_angles.append([e.distance_ecl, e.angle_ecl.rad, planet])
    planet_angles = sorted(planet_angles)

    BG = 'BLACK'
    FG = 'WHITE'

    xo, yo = 200, 300//2
    r = 260//2
    zodiac_r = r-5
    planet_r_step = zodiac_r // (1+len(planet_angles))

    dd.clear()
    dd.fill(BLACK)
    dd.circle(xo, yo, r, WHITE)


    dd.circle(xo, yo, r-10, WHITE)

    for i in range(6):
        a = math.radians((i * 30))
        x, y = int(r*math.cos(a)), int(r*math.sin(a))
        dd.line(xo+x, yo+y,  xo-x, yo-y, WHITE)

    for i, sy in enumerate(reversed(zodiac)):
        a = math.radians((((i+1) * 30) - 15) - 90)

        SymbolWidget(h, (xo+int(zodiac_r*math.cos(a))-4, yo+int(zodiac_r*math.sin(a))-4), (8,9), sy, c=FG, bg=BG,).draw()

    for i, p in enumerate(planet_angles):
        p_r = ((i+1) * planet_r_step)+4
        __, a, sy = p
        a = a + math.radians(-(90))
        SymbolWidget(h, ((xo-4)-int(p_r*math.cos(a)), yo+int(p_r*math.sin(a))-4), (8,9), sy, c=FG, bg='RED', ).draw()

        
        #dd.text(
        #        planet_symbols[zodiac[i]], va='center', ha='center')

    #for ix, s in enumerate(SymbolWidget.SYMBOLS):
    #    x = 10+(ix*15)
    #    SymbolWidget(h, (x, 50), (8,9), s).draw()
    #    SymbolWidget(h, (x, 65), (8,9), s, draw_bg=True).draw()
    #    SymbolWidget(h, (x, 80), (8,9), s, bg='BLACK').draw()


    h.draw()

class Heliocentric:
    pass

class Areocentric:
    pass
