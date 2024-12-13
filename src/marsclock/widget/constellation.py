import os
from marsclock.mathutils import MetaRand
try:
    import json
except ImportError:
    import ujson as json



constellations_resource = '/resources/constellations'


class ConstellationWidget:
    def __init__(self, display, size, position=(15, 85)):
        self.display = display
        self.epd = display.epd
        self.position = position
        self.constellations = ['/'.join([constellations_resource, p]) for p in os.listdir(constellations_resource)]
        self.constellation_file = None

    def draw(self):
        self.constellation_file = self._select_random_constellation()
        self._draw_constellations(self.constellation_file)

    def _select_random_constellation(self):
        n = MetaRand.rand_int(len(self.constellations))
        return self.constellations[n]

    def _draw_constellations(self, constellation_file):
        chart = json.load(open(constellation_file))
        x0, y0 = self.position
        for a, b in chart['links']:
            (x1, y1), (x2, y2) = chart['stars'][a], chart['stars'][b]
            self.epd.line(x0+x1, y0+y1, x0+x2, y0+y2, CK)
        r0 = 3
        r1 = r0+2
        # Erase the border around the stars
        for n, (x, y) in chart['stars'].items():
            if not n.startswith('OFF'):
                self.epd.ellipse(x0+x, y0+y, r1, r1, CW, True)
        # Draw the stars
        for n, (x, y) in chart['stars'].items():
            if not n.startswith('OFF'):
                self.epd.ellipse(x0+x, y0+y, r0, r0, CK, True)

        for m, x, y in chart['annotations']:
            self.epd.text(m, x0+x, y0+y, CK)
        for m, x, y in chart['titles']:
            self.epd.text(m, x0+x, y0+y, CK)