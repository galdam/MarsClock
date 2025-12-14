__ = '''
from marsclock import config
from marsclock.astro import astrotime


class RtcWrapperAbs:
    def __init__(self):
        self.timezone = config.EARTH_TIMEZONE
        self.dst_mode = config.EARTH_DST_MODE
        self.earth_time, self.mars_time = None, None
        self.earth_time_mask, self.mars_time_mask = None, None
        self.refresh_time()

    @staticmethod
    def compare_datetimes(time_a, time_b):
        # TODO: At the end of DST, the hour will still the same
        if time_a is None:
            return astrotime.DateTimeTup(*[False for b in time_b.to_tuple()])
        return astrotime.DateTimeTup(*[a == b for a, b in zip(time_a.to_tuple(), time_b.to_tuple())])

    def refresh_time(self):
        et = self._get_time()
        mt = et.to_marstime()
        self.earth_time_mask = self.compare_datetimes(self.earth_time, et)
        self.mars_time_mask = self.compare_datetimes(self.mars_time, mt)
        self.earth_time = et
        self.mars_time = mt

    def _get_time(self):
        return astrotime.EarthDateTime(*self._get_time_tup(),
                                       tm_tzone=self.timezone, tm_dst=self.dst_mode)

    def _get_time_tup(self):
        raise NotImplementedError()

    def set_time(self, tt):
        raise NotImplementedError()
'''
