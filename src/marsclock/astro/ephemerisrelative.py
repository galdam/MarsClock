from marsclock.astro.ephemeris import Ephemeris

from marsclock.astro.astrotime import EarthDateTime, j2kdelta_2_mars_standard_time, j2kdelta_2_epoch_tc_seconds
import marsclock.helpers.math.mathplus as math
from marsclock.helpers.math.angle import Angle, anglehelpers

__ = """
class EphemerisLocal(Ephemeris):
    def __init__(self, planet, j2k, longitude, latitude, elevation=0):
        super().__init__(planet, j2k)
        self.longitude = longitude
        self.latitude = latitude
        self.elevation = elevation
"""


class EphemerisRelative:
    """"""
    def __init__(self, observer, j2k, target=None, location=None, et_kwargs=None):
        self.observer=observer
        self.observer_e = Ephemeris(planet=observer, j2k=j2k)
        self.j2k = j2k
        self.target=target if target else 'Sun'
        self.target_e = None if self.target == 'Sun' else Ephemeris(planet=self.target, j2k=j2k)
        self.location = self.__class__.validate_location(location)
        self.et_kwargs = dict() if et_kwargs is None else et_kwargs

    @staticmethod
    def validate_location(location):
        if location is None:
            return location
        longitude = location['longitude']
        #if not isinstance(longitude, Angle):
        #    longitude = Angle(deg=longitude)
        latitude = location['latitude']
        #if not isinstance(latitude, Angle):
        #    latitude = Angle(deg=latitude)
        elevation = location.get('elevation', 0)
        return {'longitude': longitude, 'latitude': latitude, 'elevation': elevation}

    @property
    def latitude(self):
        return Angle(self.location['latitude'])

    @property
    def longitude(self):
        return Angle(self.location['longitude'])

    @property
    def ecliptic_vector(self):
        target_position_ecliptic = self.target_e.position_ecliptic if self.target_e is not None else (0, 0, 0)
        return tuple([t - o for t, o in zip(target_position_ecliptic, self.observer_e.position_ecliptic)])

    @property
    def position_equatorial(self):
        return ecliptic_2_equatorial(*self.ecliptic_vector, self.observer_e.obliquity)
    
    @property
    def angle_ecl(self):
        x, y, z = self.ecliptic_vector
        return Angle(rad=math.atan2(y, x))

    @property
    def distance_ecl(self):
        x, y, z = self.ecliptic_vector
        # v = math.sqrt(x*x + y*y)
        v = math.hypot(x, y)
        return v

    @property
    def spherical_equatorial(self):
        r, ra, dec = rectangular_2_spherical(*self.position_equatorial)
        return r, ra, dec

    @property
    def ha_az_alt(self):
        return calc_ha_az_alt(self)

    @property
    def meridian_mean_sidereal_time(self):
        if self.observer == 'Earth':
            return Angle(deg=j2k_2_gmst(self.j2k))
        raise NotImplementedError()

    @property
    def local_mean_sidereal_time(self):
        lst = Angle(deg=(self.meridian_mean_sidereal_time.deg + self.longitude.deg) 
                    % 360.0)
        return lst

    @property
    def meridian_mean_solar_time(self):  
        """
        Time based on the fictitious mean Sun crossing the meridian
        On Earth: Greenwich Mean Solar Time, GMST
        """ 
        if self.observer == 'Earth':
            mst = self.j2k
        elif self.observer == 'Mars':
            mst = j2kdelta_2_mars_standard_time(self.j2k)
        else:
            raise NotImplementedError()
        return Angle(deg = ((mst * 360) % 360))

    @property
    def local_mean_solar_time(self):
        """
        LMST, Local Mean Solar Time
        Time based on the fictitious mean Sun crossing a local meridian
        """
        return Angle(deg=(self.meridian_mean_solar_time.deg + self.longitude.deg) % 360.0)
    
    @property
    def local_true_solar_time(self):
        """
        LTST, Local True Solar Time, Apparent Solar Time
        Local True Solar Time = Local Mean Solar Time + Equation of Time
        The Local Mean Solar Time for a given planetographic longitude, Λ, in degrees west, 
        is easily determined by offsetting from the mean solar time on the prime meridian.
        """
        return Angle(deg=(self.local_mean_solar_time.deg + self.observer_e.equation_of_time.deg))

    @property
    def subsolar_longitude(self):
        """
        Λs = MST (360° / 24 h) + EOT + 180° = MST (15° / h) + EOT + 180°
        """
        return Angle(deg=(self.meridian_mean_solar_time.deg + self.observer_e.equation_of_time.deg + 180) % 360)

        #if self.observer == 'Earth':
        #    return j2k_2_earth_local_mean_solar_time(self.j2k, self.longitude.deg)
        #elif self.observer == 'Mars':
        #    return j2k_2_mars_local_mean_solar_time(self.j2k, self.longitude.deg)
        #else:
        #    raise NotImplementedError()
        
    @property
    def hour_angle(self):
        "Ha = Λ - Λs"
        return Angle(deg=self.longitude.deg - self.subsolar_longitude.deg)
    
    @property
    def local_solar_zenith_angle(self):
        """
        For any given point on Mars's surface, we want to determine the angle of the sun. The zenith angle is:
        Z = arccos (sin δs sin φ + cos δs cos φ cos H)
        where 
        φ  = planetographic latitude, 
        Λ  = planetographic longitude, 
        H = Λ - Λs = hour angle,
        δs = solar declination
        """
        Z = math.acos(math.sin(self.observer_e.solar_declination.rad) * math.sin(self.latitude.rad)
                      + math.cos(self.observer_e.solar_declination.rad) * math.cos(self.latitude.rad)
                      * math.cos(self.hour_angle.rad))
        return Angle(rad=Z)

    @property
    def local_solar_elevation(self):
        """
        For any given point on Mars's surface, we want to determine the angle of the sun. The zenith angle is:
        Z = arccos (sin δs sin φ + cos δs cos φ cos H)
        where φ is the planetographic latitude, Λ is the planetographic longitude, and H the hour angle, Λ - Λs.
        The solar elevation is simply 90° - Z.
        """
        return Angle(deg=90-self.local_solar_zenith_angle.deg)
    
    @property
    def local_solar_azimuth(self):
        """
        The second element of the sun's location as seen from a point on Mars's surface is its azimuth, i.e., compass angle relative to due north.
        A = arctan (sin H / (cos φ tan δs - sin φ cos H)) 
        """
        A = math.atan2(math.sin(self.hour_angle.rad), # /
                       (math.cos(self.latitude.rad) * math.tan(self.observer_e.solar_declination.rad) 
                        - math.sin(self.latitude.rad) * math.cos(self.hour_angle.rad)))
        return Angle(rad=A)

    @property
    def transit_arc(self):
        r, ra, dec = self.spherical_equatorial
        if (abs(dec.deg + self.latitude.deg) > 90) | (abs(dec.deg - self.latitude.deg) > 90):
            return None
        return Angle(rad=math.acos(-math.tan(dec.rad) * math.tan(self.latitude.rad)))

    @property
    def zenith(self):
        r, ra, dec = self.spherical_equatorial
        return Angle(deg=90 - abs(dec.deg - self.latitude.deg))

    @property
    def rise_elevation_transit_set(self):
        r, ra, dec = self.spherical_equatorial
        ha, az, alt = self.ha_az_alt
        w0 = Angle(rad=math.acos(-math.tan(dec.rad) * math.tan(self.latitude.rad)))
        w = sidereal_2_clock(w0)

        max_altitude = Angle(deg=90 - abs(dec.deg - self.latitude.deg))

        transit = EarthDateTime(tm_sec=int(j2kdelta_2_epoch_tc_seconds(self.j2k) - sidereal_2_clock(ha)), **self.et_kwargs)
        
        #transit = EarthDateTime(tm_sec=int(et.epoch_tc_seconds - sidereal_2_clock(ha)))
                #day * ((ha.deg / SIDEREAL_RATE) / 360))))
        et_rise = EarthDateTime(tm_sec=int(transit.epoch_tc_seconds - w), **self.et_kwargs)
        et_set = EarthDateTime(tm_sec=int(transit.epoch_tc_seconds + w), **self.et_kwargs)

        rets_data = {'rise': None, 'set': None, 
                     'elevation': max_altitude, 'transit': None, 
                     'w0': w0,
                     'w': w,
                     'spherical_equatorial': {'r':r, 'ra':ra, 'dec':dec},
                     'ha_az_alt': {'ha':ha, 'az':az, 'alt': alt},
                     'state': None}

        if abs(dec.deg - self.latitude.deg) > 90:  # Never-rise
            rets_data['state'] = 'Never-rise'
        elif abs(dec.deg + self.latitude.deg) > 90:  # Circumpolar
            rets_data['state'] = 'Circumpolar'
        else:
            rets_data['transit'] = transit
            rets_data['rise'] = et_rise
            rets_data['set'] = et_set
        return rets_data
    
    def next_twilights(self):
        ets = self.rise_elevation_transit_set
        if ets['state'] is not None:
            return None
        if ets['rise'].j2kdelta > self.j2k:
            return [('rise', ets['rise']), ('set', ets['set'])]
        
        er = EphemerisRelative(
            observer=self.observer,
            target=self.target,
            j2k=self.j2k+1,
            location=self.location,
            et_kwargs=self.et_kwargs
        )
        etsn = er.rise_elevation_transit_set
        if etsn['state'] is not None:
            return None
        
        if ets['set'].j2kdelta > self.j2k:
            return [('set', ets['set']), ('rise', etsn['rise'])]
        
        return [('rise', etsn['rise']), ('set', etsn['set'])]

    __ = """
    @property
    def apparent_magnitude(self):
        r_vec = .array(sun_to_mars)
        delta_vec = np.array(earth_to_mars)
        return 1"""


def calc_ha_az_alt(ephem_rel):
    #def get_relative_pos(observer_ephem, target_planet):
    #    target_ephem = None if (target_planet == 'Sun') else ephemeris.Ephemeris(target_planet, observer_ephem.j2k)
    #    return RelativeEphemeris(observer_ephem, target_ephem).spherical_equitorial
    r, ra, dec = ephem_rel.spherical_equatorial
    lst = ephem_rel.local_mean_sidereal_time

    # Hour Angle
    hr_angle = Angle(rad=lst.rad - ra.rad)

    lat_rad = ephem_rel.latitude.rad

    # Altitude
    alt = Angle(rad=(
        math.asin(
            math.sin(dec.rad) * math.sin(lat_rad)
            + math.cos(dec.rad) * math.cos(lat_rad) * math.cos(hr_angle.rad))))

    # Azimuth
    cos_az = (math.sin(dec.rad) - math.sin(alt.rad) * math.sin(lat_rad)) / (math.cos(alt.rad) * math.cos(lat_rad))
    sin_az = -math.cos(dec.rad) * math.sin(hr_angle.rad) / math.cos(alt.rad)
    az = Angle(deg=((math.degrees(math.atan2(sin_az, cos_az))) + 360) % 360)
    return hr_angle, az, alt


def j2k_2_gmst(j2k):
    # Get the greenwich mean siderial time for earth
    T = j2k / 36525.0
    gmst = 280.46061837 + 360.98564736629 * j2k + 0.000387933 * T ** 2 - T ** 3 / 38710000.0
    gmst_deg = gmst % 360.0
    return gmst_deg

__ = """
def j2k_2_earth_local_mean_solar_time(j2k, lon_deg):
    # Get the mean solar time for earth and add the longitude
    gmst_deg = j2k_2_gmst(j2k)
    lst = Angle(deg=(gmst_deg + lon_deg) % 360.0)
    return lst"""


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
