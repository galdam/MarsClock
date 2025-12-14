import marsclock.helpers.math.mathplus as math
from marsclock.astro.astrotime import EarthDateTime





def _ts2human(ts) -> str:
    try:
        from datetime import datetime
        return str(datetime.fromtimestamp(ts))
    except ImportError as err:
        return str(f'TS:{ts}')


def j2ts(j):
    """

    Args:
        j:

    Returns:

    """
    return (j - 2440587.5) * 86400


def ts2j(ts) -> float:
    """

    Args:
        ts:

    Returns:

    """
    return ts / 86400.0 + 2440587.5


def _j2human(j) -> str:
    ts = j2ts(2451545.0 + j)
    return f'{j} = {_ts2human(ts)}'


def _deg2human(deg):
    x = int(deg * 3600.0)
    num = f'∠{deg:.3f}°'
    rad = f'∠{math.radians(deg):.3f}rad'
    human = f'∠{x // 3600}°{x // 60 % 60}′{x % 60}″'
    return f'{rad} = {human} = {num}'


planetary_data = {
    'Earth': {
        'anomaly_epoch': 357.5291,
        'angular_speed': 0.98560028,
    },
    'Mars': {
        'anomaly_epoch': 19.3871,
        'angular_speed': 0.52402073,
    }
}




def calc_sunsetrise(julian_days, latitude, longitude, elevation=0.0, debug=False):
    # Mean solar time
    solar_time = (julian_days) - longitude / 360.0
#+ 0.0009
    # Solar mean anomaly
    solar_anomaly_deg = math.fmod(357.5291 + 0.98560028 * solar_time, 360)
    solar_anomaly_rad = math.radians(solar_anomaly_deg)

    # Equation of the center
    equation_of_centre_coefficient = 1.9148
    center_deg = (equation_of_centre_coefficient * math.sin(solar_anomaly_rad)
                  + 0.02 * math.sin(2 * solar_anomaly_rad)
                  + 0.0003 * math.sin(3 * solar_anomaly_rad))

    # Ecliptic longitude
    perihelion = 102.9372
    ecliptic_deg = math.fmod(solar_anomaly_deg + center_deg + 180.0 + perihelion, 360)
    ecliptic_rad = math.radians(ecliptic_deg)

    # Solar transit (julian date)
    solar_transit = (#2451545.0 +
            solar_time + 0.0053 * math.sin(solar_anomaly_rad)
            - 0.0069 * math.sin(2 * ecliptic_rad))

    # Declination of the Sun
    maximal_tilt = 23.4397
    declination_sin = math.sin(ecliptic_rad) * math.sin(math.radians(maximal_tilt))
    declination_cos = math.cos(math.asin(declination_sin))

    # Hour angle
    some_cos = ((math.sin(math.radians(-0.833 - 2.076 * math.sqrt(elevation) / 60.0))
                 - math.sin(math.radians(latitude)) * declination_sin)
                / (math.cos(math.radians(latitude)) * declination_cos))


    if debug:
        print(f'Latitude               f       = {_deg2human(latitude)}')
        print(f'Longitude              l_w     = {_deg2human(longitude)}')
        # print(f'Now                    ts      = {_ts2human(current_timestamp)}')
        # print(f'Julian date            j_date  = {J_date:.3f} days')
        print(f'Julian day             n       = {julian_days:.3f} days')
        print(f'Mean solar time        J_      = {solar_time:.9f} days')
        print(f'Solar mean anomaly     M       = {_deg2human(solar_anomaly_deg)}')
        print(f'Equation of the center C       = {_deg2human(center_deg)}')
        print(f'Ecliptic longitude     L       = {_deg2human(ecliptic_deg)}')
        print(f'Solar transit time     J_trans = {_j2human(solar_transit)}')


    # Value error occurs if the sun does not cross the horizon on the given day.
    try:
        w0_radians = math.acos(some_cos)
    except ValueError:
        return None, None
    w0_degrees = math.degrees(w0_radians)  # 0...180

    j_rise = (solar_transit - w0_degrees / 360)
    j_set = (solar_transit + w0_degrees / 360)


    if debug:
        print(f'Hour angle             w0      = {_deg2human(w0_degrees)}')
        print(f'Sunrise                j_rise  = {_j2human(j_rise)}')
        print(f'Sunset                 j_set   = {_j2human(j_set)}')
        dl_h = w0_degrees / (180 / 24)
        dl_min = 60 * (dl_h % 1)
        dl_sec = 60 * (dl_min % 1)
        print(f'Day length                       {math.floor(dl_h)} : {math.floor(dl_min)} : {math.floor(dl_sec)}')

    return j_rise, j_set


def julian_timestamp_to_earthtime(timestamp, tm_tzone, tm_dst):
    if timestamp is None:
        return None
    hour = timestamp % 1 * 24
    d, h, m, s = int(timestamp), int(hour), int(hour * 60.0) % 60, int(hour * 36e2) % 60
    return EarthDateTime(tm_sec=((d) * 86400) + (h * 60 * 60) + (m * 60) + s + 43200, tm_tzone=tm_tzone, tm_dst=tm_dst)


def epoch_days_to_sun_times(latitude, longitude, epoch_days, tm_tzone, tm_dst):
    sr, ss = calc_sunsetrise(epoch_days-1, latitude, longitude, elevation=0)
    return [(julian_timestamp_to_earthtime(sr, tm_tzone, tm_dst), 'sunrise'),
            (julian_timestamp_to_earthtime(ss, tm_tzone, tm_dst), 'sunset')]



def next_suntimes(et, latitude, longitude):
    sun_times = [s for s in epoch_days_to_sun_times(latitude, longitude, et.epoch_tc_days, et.tm_tzone, et.tm_dst)
                 if s[0] is not None and s[0] > et]
    if len(sun_times) < 2:
        sun_times += [s for s in epoch_days_to_sun_times(latitude, longitude, et.epoch_tc_days+1, et.tm_tzone, et.tm_dst)
                      if s[0] is not None and s[0] > et]
    return sun_times[:2]
