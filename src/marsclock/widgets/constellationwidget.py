import ujson as json
import random


class ConstellationWidget:
    def __init__(self, epd_device, position):
        self.epd_device = epd_device
        self.position = position

    @property
    def constellations(self):
        return [
            'bootes', 'cepheus', 'draco',
            'gemini', 'orion', 'ursaminor']

    def pick_constellation(self):
        return random.choice(self.constellations)

    def draw(self, constellation):
        x0, y0 = self.position
        chart = json.load(open(f'data/starcharts/{constellation}.json'))
        for a, b in chart['links']:
            (x1, y1), (x2, y2) = chart['stars'][a], chart['stars'][b]
            self.epd_device.line(x1=x0+x1, y1=y0+y1, x2=x0+x2, y2=y0+y2, c='B')
        r0 = 3
        r1 = r0+2
        # Erase the border around the stars
        for n, (x, y) in chart['stars'].items():
            if not n.startswith('OFF'):
                self.epd_device.ellipse(x=x0+x, y=y0+y, xr=r1, yr=r1, c='W', f=True)
        # Draw the stars
        for n, (x, y) in chart['stars'].items():
            if not n.startswith('OFF'):
                self.epd_device.ellipse(x=x0+x, y=y0+y, xr=r0, yr=r0, c='R', f=True)

        for m, x, y in chart['annotations']:
            self.epd_device.text(s=m, x=x0+x, y=y0+y, c='B')
        for m, x,y in chart['titles']:
            self.epd_device.text(s=m, x=x0+x, y=y0+y, c='B')