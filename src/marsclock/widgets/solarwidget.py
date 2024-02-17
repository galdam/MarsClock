import math


class SolarWidget:
    info = {
        'sun_center': [0.08130119975484532, -0.035981667846039095],
        'earth_center': [0.08364782435742593, -0.046144978189297144],
        'earth_radius': [0.6249367624495906, 0.6250271141235764],
        'earth_ny_radians': 1.7480794922079936,
        'mars_center': [0, 0],
        'mars_radius': [0.951442924451731, 0.9487822885402397],
        'mars_ny_radians': 1.2916927448127111
    }

    def __init__(self, epd_device, size, position, flip_y=True):
        self.epd_device = epd_device
        self.size = size
        self.scale = self.size//2
        self.position = position
        self.origin = self.position[0] + self.scale, self.position[1] + self.scale
        self.flip_y = flip_y
        self.planet_size = 4

    def draw(self, earth_time, mars_time):
        #ps = self.planet_size
        #x, y, xr, yr, c, f

        earth_days = earth_time.tm_yday
        mars_days = mars_time.tm_yday

        # Draw the sun in
        self.epd_device.ellipse(**self.sun(), c='R', f=True)
        for planet, days in [('mars', mars_days), ('earth', earth_days)]:
            # Draw the path
            self.epd_device.ellipse(**self.planet_path(planet), c='B')
            # Erase the area around the planet
            self.epd_device.ellipse(
                **self.planet_loc(planet, days),
                xr=self.planet_size+3, yr=self.planet_size+3,
                c='W', f=True)
            # Draw the planet
            self.epd_device.ellipse(
                **self.planet_loc(planet, days),
                xr=self.planet_size, yr=self.planet_size,
                c='R', f=True)

    def _y(self, y):
        """
        Calculations were all made with a bottom-left origin, whereas screens use a top-left origin.
        The easiest fix is to flip the y axis.
        """
        return self.origin[1] + (-1*(y-self.origin[1])) if self.flip_y else y
    
    def sun(self):
        sc = self.info['sun_center']
        return {
            'x': int(self.origin[0] + (sc[0] * self.scale)),
            'y': self._y(int(self.origin[1] + (sc[1] * self.scale))),
            'xr': self.planet_size,
            'yr': self.planet_size,
        }

    def planet_path(self, planet):
        pcenter = self.info[f"{planet}_center"]
        pradius = self.info[f"{planet}_radius"]
        return {
            'x': int(self.origin[0] + (pcenter[0] * self.scale)),
            'y': self._y(int(self.origin[1] + (pcenter[1] * self.scale))),
            'xr': int(pradius[0] * self.scale),
            'xy': int(pradius[1] * self.scale),
        }

    def planet_loc(self, planet, dayofyear):
        yearlen = 365 if planet == 'earth' else 668
        cx, cy, rx, ry = self.planet_path(planet)
        angle = _radians_on_day(self.info[f'{planet}_ny_radians'], yearlen, dayofyear)
        lx, ly = _point_on_ellipse((cx, self._y(cy)), (rx, ry), angle)
        return {'x': lx, 'y': self._y(ly),}


def _radians_on_day(ny_radians, yearlen, dayofyear):
    return ny_radians + ((2*math.pi) * (dayofyear / yearlen))


def _point_on_ellipse(center, radius, angle):
    """Angle in radians"""
    center_x, center_y = center
    x_radius, y_radius = radius
    x = center_x + x_radius * math.cos(angle)
    y = center_y + y_radius * math.sin(angle)
    return int(x), int(y)