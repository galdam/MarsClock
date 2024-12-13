import marsclock.helpers.math.mathplus as math


class Solar:
    CELESTIAL_INFO = {
        'Mercury': {
            'amp': -0.377502270936507,
            'ang_freq': 0.07142478608950242,
            'phase': 1.2252323492224204,
            'offset': -0.07107779149567722,
        },
        'Venus': {
            'amp': -0.7226799580838549,
            'ang_freq': 0.027962451781572622,
            'phase': 0.020580357602021464,
            'offset': -0.00031182020335230763,
        },
        'Earth': {
            'amp': 0.9998620197470092,
            'ang_freq': 0.017202123779253432,
            'phase': 1.744853901416548,
            'offset': -0.009245497345189674,
        },
        'Mars': {
            'amp': 1.5165855910833743,
            'ang_freq': 0.00914609795171124,
            'phase': -0.08393127577167812,
            'offset': -0.0559503195916683,
        },
        'Jupiter': {
            'amp': 5.196462311235087,
            'ang_freq': 0.0014501525979470108,
            'phase': 0.5987951168854406,
            'offset': -0.2310134925080858,
        },
        'Saturn': {
            'amp': 9.527230836935619,
            'ang_freq': 0.0005840839302638456,
            'phase': 0.8769933676327171,
            'offset': -0.3718816100969191,
        },
    }

    info = {
        'sun_center': [0.08130119975484532, -0.035981667846039095],
        'earth_center': [0.08364782435742593, -0.046144978189297144],
        'earth_radius': [0.6249367624495906, 0.6250271141235764],
        'earth_ny_radians': 1.7480794922079936,
        'mars_center': [0, 0],
        'mars_radius': [0.951442924451731, 0.9487822885402397],
        'mars_ny_radians': 1.2916927448127111
    }

    def __init__(self, position, size, flip_y=True):
        self.size = size
        self.scale = self.size // 2
        self.position = position
        self.origin = self.position[0] + self.scale, self.position[1] + self.scale
        self.flip_y = flip_y

    def _y(self, y):
        return self.origin[1] + (-1 * (y - self.origin[1])) if self.flip_y else y

    def sun(self):
        sc = self.info['sun_center']
        return (int(self.origin[0] + (sc[0] * self.scale)),
                self._y(int(self.origin[1] + (sc[1] * self.scale))))

    def planet_path(self, planet):
        pcenter = self.info[f"{planet}_center"]
        pradius = self.info[f"{planet}_radius"]
        return [
            int(self.origin[0] + (pcenter[0] * self.scale)),
            self._y(int(self.origin[1] + (pcenter[1] * self.scale))),
            int(pradius[0] * self.scale),
            int(pradius[1] * self.scale), ]

    def planet_loc(self, planet, dayofyear):
        yearlen = 365 if planet == 'earth' else 668
        cx, cy, rx, ry = self.planet_path(planet)
        angle = _radians_on_day(self.info[f'{planet}_ny_radians'], yearlen, dayofyear)
        lx, ly = math.point_on_ellipse((cx, self._y(cy)), (rx, ry), angle)
        return lx, self._y(ly)


def _radians_on_day(ny_radians, yearlen, dayofyear):
    return ny_radians + ((2 * math.pi) * (dayofyear / yearlen))



