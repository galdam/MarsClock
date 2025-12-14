"""
A wrapper that keeps track of the current time and what's changed since the time was last checked.
"""

from marsclock import config
from marsclock.astro import astrotime


class RtcWrapper:
    def __init__(self, rtc):
        self.rtc = rtc
        self.timezone = config.EARTH_TIMEZONE
        #self.dst_mode = config.EARTH_DST_MODE
        self.earth_time, self.mars_time = None, None
        self.earth_time_mask, self.mars_time_mask = None, None
        self.refresh_time()

    @staticmethod
    def compare_datetimes(time_a, time_b):
        """
        Create a boolean array of
        Args:
            time_a:
            time_b:
        Returns: DateTimeTup(bool)
        """
        # TODO: At the end of DST, the hour will still the same
        if time_a is None:
            return astrotime.DateTimeTup(*[False for b in time_b.to_tuple()])
        
        tup_a, tup_b = time_a.to_tuple(), time_b.to_tuple()
        return astrotime.DateTimeTup(*[tup_a[:i] == tup_b[:i] for i in range(1, len(tup_a)+1)])
        # return astrotime.DateTimeTup(*[a == b for a, b in zip(time_a.to_tuple(), time_b.to_tuple())])

    def refresh_time(self):
        """
        Refresh the
        Returns: None
        """
        et = self._get_time()
        mt = et.to_marstime()
        self.earth_time_mask = self.compare_datetimes(self.earth_time, et)
        self.mars_time_mask = self.compare_datetimes(self.mars_time, mt)
        self.earth_time = et
        self.mars_time = mt

    def _get_time_tup(self):
        """

        Returns:

        """
        return self.rtc.get_time_tup()[:6]

    def _get_time(self):
        """

        Returns:

        """
        return astrotime.EarthDateTime(
            *self._get_time_tup(),
            tm_tzone=self.timezone,)

    # def set_time(self, tt):
    #    raise NotImplementedError()

