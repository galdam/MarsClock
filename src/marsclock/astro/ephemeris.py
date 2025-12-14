"""
Formulas for calculating the approximate positions
are based on the  following:
https://ssd.jpl.nasa.gov/planets/approx_pos.html

"""


import marsclock.helpers.math.mathplus as math
from marsclock.helpers.math.angle import Angle, anglehelpers

# a: semi-major axis [au, au/century]
# e: eccentricity [0-1]
# I: inclination [degrees, degrees/century]
# L: mean longitude [degrees, degrees/century]
# w_conj: longitude of perihelion [degrees, degrees/century]
# omega: longitude of the ascending node [degrees, degrees/century]
_keplerian_elements_v1 = {
    #  a             e               I                L                long.peri.      long.node.
    #  au, au/Cy     rad, rad/Cy     deg, deg/Cy      deg, deg/Cy      deg, deg/Cy     deg, deg/Cy
    "Mercury": [
        [0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593],
        [0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689,  -0.12534081],],
    "Venus": [
        [0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255],
        [0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418]],
    "Earth": [
        [1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0],
        [0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],],
    "Mars": [
        [1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891],
        [0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],],
    "Jupiter": [
        [5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909],
        [-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],],
    "Saturn": [
        [9.53667594, 0.05386179,  2.48599187, 49.95424423, 92.59887831, 113.66242448],
        [-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],],
}

_keplerian_elements_v2 = {
    'Mercury': [
        [0.38709843, 0.20563661, 7.00559432, 252.25166724, 77.45771895, 48.33961819],
        [0.00000000, 0.00002123, -0.00590158, 149472.67486623, 0.15940013, -0.12214182]],
    'Venus': [
        [0.72332102, 0.00676399, 3.39777545, 181.97970850, 131.76755713, 76.67261496],
        [-0.00000026, -0.00005107, 0.00043494, 58517.81560260, 0.05679648, -0.27274174]],
    'Earth': [
        [1.00000018, 0.01673163, -0.00054346, 100.46691572, 102.93005885, -5.11260389],
        [-0.00000003, -0.00003661, -0.01337178, 35999.37306329, 0.31795260, -0.24123856]],
    'Mars': [
        [1.52371243, 0.09336511, 1.85181869, -4.56813164,  -23.91744784, 49.71320984],
        [0.00000097, 0.00009149, -0.00724757, 19140.29934243, 0.45223625, -0.26852431]],
    'Jupiter': [
        [5.20248019, 0.04853590, 1.29861416, 34.33479152, 14.27495244, 100.29282654],
        [-0.00002864, 0.00018026, -0.00322699, 3034.90371757, 0.18199196, 0.13024619],
        [-0.00012452, 0.06064060, -0.35635438, 38.35125000],
    ],
    'Saturn': [
        [9.54149883, 0.05550825, 2.49424102, 50.07571329, 92.86136063, 113.63998702],
        [-0.00003065, -0.00032044, 0.00451969, 1222.11494724, 0.54179478, -0.25015002],
        [0.00025899, -0.13434469, 0.87320147, 38.35125000],
    ],
    'Uranus': [
        [19.18797948, 0.04685740, 0.77298127, 314.20276625, 172.43404441, 73.96250215],
        [-0.00020455, -0.00001550, -0.00180155, 428.49512595, 0.09266985, 0.05739699],
        [0.00058331, -0.97731848, 0.17689245, 7.67025000],
    ],
    'Neptune': [
        [30.06952752, 0.00895439, 1.77005520, 304.22289287, 46.68158724, 131.78635853],
        [0.00006447, 0.00000818, 0.00022400, 218.46515314, 0.01009938, -0.00606302],
        [-0.00041348, 0.68346318, -0.10162547, 7.67025000],
    ],
}

_obliquities = {
    "Mercury": Angle(deg=0.034),
    "Venus": Angle(deg=177.4),     # Retrograde rotation
    "Earth": Angle(deg=23.4397),
    "Mars": Angle(deg=25.19),
    "Jupiter": Angle(deg=3.13),
    "Saturn": Angle(deg=26.73),
    "Uranus": Angle(deg=97.77),    # Extreme tilt, rotates on its side
    "Neptune": Angle(deg=28.32),
}


class Ephemeris:

    def __init__(self, planet, j2k, longitude=None, latitude=None):
        # # 1800.AD - 2050.AD
        # self._keplerian_elements = _keplerian_elements_v1
        # if not (-73049 < j2k < 18262):
        #     print("WARNING: Approximations are only valid between 1800 AD and 2050 AD")

        # 3000.BC - 3000.AD
        self._keplerian_elements = _keplerian_elements_v2

        # Verify the planet is valid
        if planet not in self._keplerian_elements:
            raise ValueError(f"No data for planet: {planet}")
        self.planet = planet

        # Convert the date to fractions of a century
        self.j2k = j2k
        self.tcy = self._j2k_to_tcy(self.j2k)

        if (longitude is None or latitude is None) and not (longitude is None and latitude is None):
            raise ValueError("If both longitude and latitude must both be set if either is set.")
        self._longitude, self._latitude = longitude, latitude

        # Prepare the first elements
        self._elements = self._keplerian_elements_on_date(self.planet, self.tcy)

    @staticmethod
    def _j2k_to_tcy(j2k):
        """
        Convert j2k (days since the J2k epoch) to fractions of a century
        """
        return j2k / 36525

    def _keplerian_elements_on_date(self, planet, tcy):
        """
        Load the keplerian approximations for the date.
        """
        header = ['a_au', 'ec', 'I_deg', 'L_deg', 'long.peri_deg', 'long.node_deg']
        p = self._keplerian_elements[planet]
        ele = {h: zero + (cy * tcy) for h, zero, cy in zip(header, p[0], p[1])}
        mod_header = ['b', 'c', 's', 'f']
        try:
            ele.update(zip(mod_header, p[2]))
        except IndexError:
            ele.update(zip(mod_header, [0]*len(mod_header)))
        ele.update({k.rsplit('_', 1)[0]: Angle(deg=v) for k, v in ele.items() if k.endswith('deg')})
        ele['obliquity'] = _obliquities[planet]
        return ele

    __ = """
    def obliquity_of_the_ecliptic(self):
        \"""ϵ\"""
        return Angle(deg=23.4393)
    """

    @property
    def longitude(self):
        if self._longitude is None:
            raise ValueError("Local position has not been provided")
        return self._longitude()

    @property
    def latitude(self):
        if self._latitude is None:
            raise ValueError("Local position has not been provided")
        return self._latitude

    @property
    def a_au(self):
        """a: semi-major axis [au, au/century]"""
        return self._elements['a_au']

    @property
    def ec(self):
        """e , ec: eccentricity [0-1]"""
        return self._elements['ec']

    @property
    def L(self):
        """L: mean longitude [degrees / century]"""
        return self._elements['L']

    @property
    def I(self):
        """I: inclination [degrees, degrees/century]"""
        return self._elements['I']

    @property
    def longperi(self):
        """ϖ: longitude of perihelion [degrees, degrees/century]"""
        return self._elements['long.peri']

    @property
    def obliquity(self):
        """
        ϵ: obliquity of the ecliptic
        """
        return _obliquities[self.planet]

    @property
    def longnode(self):
        """
        Ω, omega: longitude of the ascending node [degrees, degrees/century]
        Right Ascension of Ascending Node (RAAN) [aka “RA of Node” or “O0”]
        The longitude of where the orbit crosses the equator going northward
        an angle, measured at the center of the earth, from the vernal equinox to the ascending node.
        """
        return self._elements['long.node']

    @property
    def perihelion(self):
        """
        ω: perihelion
        Compute the argument of perihelion, argument of periapsis
        (longitude of perihelion)-(longitude of the ascending node)
        """
        key = 'perihelion'
        if key not in self._elements:
            self._elements[key] = Angle(rad=(self.longperi.rad - self.longnode.rad))
        return self._elements[key]


    @property
    def mean_anomaly(self):
        # M: mean anomaly
        # 
        key = 'M'
        try:
            return self._elements[key]
        except KeyError:
            return self._elements.setdefault(
                key, Angle(deg=self._calculate_mean_anomaly_deg(
                    L=self.L.deg,
                    w_conj=self.longperi.deg,
                    T=self.tcy,
                    b=self._elements['b'],
                    c=self._elements['c'],
                    s=self._elements['s'],
                    f=self._elements['f']
                )))

    @property
    def eccentric_anomaly(self):
        k = 'E'
        try:
            return self._elements[k]
        except KeyError:
            return self._elements.setdefault(k,
                Angle(rad=self._calc_keplers_equation(self.ec, self.mean_anomaly.rad)))

    @property
    def true_anomaly(self):
        """v: True anomaly"""
        k = 'phi_rad'
        try:
            return self._elements[k]
        except KeyError:
            return self._elements.setdefault(k,
                Angle(rad=self._calc_true_anomaly_rad(
                    ec=self.ec,
                    E=self.eccentric_anomaly.rad)))

    @property
    def eq_center(self):
        k = 'eq_center'
        try:
            return self._elements[k]
        except KeyError:
            return self._elements.setdefault(k,
                Angle(rad=anglehelpers.modulo_radians_tau(self.true_anomaly.rad - self.mean_anomaly.rad)))

    @property
    def position_orbital(self):
        k = 'pos_prime'
        try:
            return self._elements[k]
        except KeyError:
            return self._elements.setdefault(k,
                self._calc_orbital_position(
                    a=self.a_au,
                    ec=self.ec,
                    E=self.eccentric_anomaly.rad))

    @property
    def position_ecliptic(self):
        k = 'pos_ecl'
        try:
            return self._elements[k]
        except KeyError:
            return self._elements.setdefault(k,
                self._calc_ecl_position(pos_prime=self.position_orbital,
                                        w=self.perihelion.rad,
                                        omega=self.longnode.rad,
                                        I=self.I.rad))


    def _rectangular_2_spherical(self, x, y, z):
        """
        Convert from rectangular coordinates (x, y, z)
        to spherical (r: radius, ra: right ascension, dec: declination)
        """
        r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
        ra = Angle(rad=math.atan2(y, x) % (2 * math.pi))
        dec = Angle(rad=math.asin(z / r))
        return r, ra, dec

    @property
    def ecliptic_spherical(self):
        r, ra, dec = self._rectangular_2_spherical(*self.position_ecliptic)
        return r, ra, dec

    @property
    def distance_ecl(self):
        return self.ecliptic_distance

    @property
    def ecliptic_distance(self):
        k = 'distance_ecl'
        try:
            return self._elements[k]
        except KeyError:
            x, y, z = self.position_ecliptic
            # v = math.sqrt(x*x + y*y)
            v = math.hypot(x, y) 
            return self._elements.setdefault(k, v)

    @property
    def angle_ecl(self):
        return self.ecliptic_longitude
    
    @property
    def ecliptic_longitude(self):
        k = 'angle_ecl'
        try:
            return self._elements[k]
        except KeyError:
            x, y, z = self.position_ecliptic
            return self._elements.setdefault(
                k,
                Angle(rad=math.atan2(y, x)))
        
    @property
    def ecliptic_latitude(self):
        return self.ecliptic_spherical[2]

    @property
    def position_equitorial(self):
        return self._calc_equitorial_position(*self.position_ecliptic)



    __ = '''
    @property
    def ecliptic_longitude(self):
        """
        Ls:
        ecliptic_longitude
        """
        key = 'ecliptic_longitude'
        if key not in self._elements:
            self._elements[key] = Angle(deg=anglehelpers.modulo_degrees_360(
                self.mean_anomaly.deg
                + self.eq_center.deg
                + 180.0
                + self.perihelion.deg))
        return self._elements[key]'''
    
    @property
    def afms(self):
        if self.planet == 'Mars':
            return Angle(deg=(270.3871 + 0.524038496 * self.j2k % 360))
        else:
            raise NotImplementedError(
                    f'Cannot calculate "Angle of Fiction Mean Sun" for planet: {self.planet}')

    @property
    def solar_longitude(self):
        if self.planet == 'Mars':
            return Angle(deg=self.afms.deg + self.eq_center.deg)
        else:
            raise NotImplementedError(
                    f'Cannot calculate "Solar longitude/ Ls" for planet: {self.planet}')
    
    @property
    def solar_declination(self):
        if self.planet == 'Mars':
            r = (math.asin(0.42565 * math.sin(self.solar_longitude.rad))
             + math.radians(0.25) * math.sin(self.solar_longitude.rad))
            return Angle(rad=r)
        else:
            raise NotImplementedError(
                    f'Cannot calculate "Solar declination / sigma s" for planet: {self.planet}')

    @property
    def equation_of_time(self):
        k = 'eot'
        try:
            return self._elements[k]
        except KeyError:
            if self.planet == 'Earth':
                eot = (0.0053 * math.sin(self.mean_anomaly.rad)
                       - 0.0069 * math.sin(2 * self.ecliptic_longitude.rad))
            elif self.planet == 'Mars':
                Ls = self.solar_longitude.rad
                eot = (math.radians(2.861) * math.sin(2*Ls) - math.radians(0.071) * math.sin(4 * Ls) 
                       + math.radians(0.002) * math.sin(6 * Ls) - self.eq_center.rad)
            else:
                raise NotImplementedError(
                    f"Cannot calculate Equation of Time for planet: {self.planet}")
            eot = Angle(rad=eot)
            #if self.planet == 'Mars'
            #x, y, z = self.position_ecl
            return self._elements.setdefault(k, eot)

    @property
    def solar_transit(self):
        solar_time = (math.floor(self.j2k) - 1) - self.longitude / 360.0
        solar_transit = solar_time + self.equation_of_time
        return solar_transit

    #@property
    #def helio_declination(self):
    #    # Declination of the Sun
    #    declination_sin = math.sin(self.ecliptic_longitude.rad) * math.sin(self.obliquity.rad)
    #    declination_cos = math.cos(math.asin(declination_sin))

    @staticmethod
    def _calculate_mean_anomaly_deg(L, w_conj, T, b, c, s, f):
        return anglehelpers.modulo_degrees_180((
            L - w_conj
            + (b * (T * T))
            + (c * math.cos(math.radians(f * T)))
            + (s * math.sin(math.radians(f * T)))
        ))

    @staticmethod
    def _calc_machin_starting_point(e, M):
        # Machin's starting point for Newton's method
        # See johndcook.com/blog/2022/11/01/kepler-newton/
        # https://www.johndcook.com/blog/2022/11/02/keplers-equation-python/
        n = math.sqrt(5 + math.sqrt(16 + 9 / e))
        a = n * (e * (n ** 2 - 1) + 1) / 6
        c = n * (1 - e)
        d = -M
        s = math.cubic_equation(a, c, d)
        return n * math.asin(s)

    @staticmethod
    def _calc_keplers_equation(ec, M, tolerance=1e-6):
        """Find E such that M = E - e sin E.
        https://github.com/dfm/kepler.py/blob/main/src/lib/main.cpp
        """
        assert (0 <= ec < 1)
        high = M > math.pi
        if high:
            M = math.tau - M
        assert (0 <= M <= math.pi), M
        f = lambda E: E - ec * math.sin(E) - M
        E = Ephemeris._calc_machin_starting_point(ec, M)
        # Newton's method
        while (abs(f(E)) > tolerance):
            E -= f(E) / (1 - ec * math.cos(E))
        if high:
            E = math.tau - E
        return E

    @staticmethod
    def _calc_true_anomaly_rad(ec, E):
        fak = math.sqrt(1.0 - ec * ec)
        phi = math.atan2(fak * math.sin(E), math.cos(E) - ec)
        return phi

    @staticmethod
    def _calc_orbital_position(a, ec, E):
        # a=semimajor axis, ec=eccentricity, E=eccentric anomaly
        # x,y = coordinates of the planet with respect to the Sun
        # http://www.jgiesen.de/kepler/kepler.html

        x = a * (math.cos(E) - ec)
        y = a * math.sqrt(1.0 - ec * ec) * math.sin(E)
        return x, y, 0

    @staticmethod
    def _calc_ecl_position(pos_prime, w, omega, I):
        """
        Converts Keplerian elements to Cartesian coordinates in the ECI frame.
        """
        sin_cos = lambda v: (math.sin(v), math.cos(v))

        x_prime, y_prime, z_prime = pos_prime

        # w = self.perihelion_rad, omega=self.longnode_rad, I=self.I_rad
        sin_w, cos_w = sin_cos(w)
        sin_omega, cos_omega = sin_cos(omega)
        sin_I, cos_I = sin_cos(I)

        x_ecl = ((cos_w * cos_omega - sin_w * sin_omega * cos_I) * x_prime
                 + (-sin_w * cos_omega - cos_w * sin_omega * cos_I) * y_prime)

        y_ecl = ((cos_w * sin_omega + sin_w * cos_omega * cos_I) * x_prime
                 + (-sin_w * sin_omega + cos_w * cos_omega * cos_I) * y_prime)

        z_ecl = ((sin_w * sin_I) * x_prime + (cos_w * sin_I) * y_prime)

        return x_ecl, y_ecl, z_ecl


    @staticmethod
    def _calc_equitorial_position(x_ecl, y_ecl, z_ecl):
        e = 23.43928

        sin_e, cos_e = math.sin(e), math.cos(e)

        x_eq = x_ecl
        y_eq = + cos_e * y_ecl - sin_e * z_ecl
        z_eq = + sin_e * y_ecl + cos_e * z_ecl
        return x_eq, y_eq, z_eq





