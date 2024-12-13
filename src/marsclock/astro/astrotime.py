"""
Many of the functions are heavily based on the python and micropython time modules,
extended to include mars times and to use a y2k epoch :
 - https://github.com/micropython/micropython/blob/master/shared/timeutils/timeutils.c
 - https://github.com/python/cpython/blob/main/Lib/calendar.py
"""
#from abc import ABCMeta, abstractmethod
from collections import namedtuple
from marsclock import config
from marsclock.astro.load_locale import get_locale
from marsclock.helpers.math.mathplus import c_divmod
from marsclock.astro.strfmtastrotime import StrFmtTime


DateTimeTup = namedtuple(
    'DateTimeTup',
    ('tm_year', 'tm_mon', 'tm_mday', 'tm_hour',
     'tm_min', 'tm_sec'))

MINUTE = 60
HOUR = 60*60
DAY = 60*60*24


class AbstractDateTime():#metaclass=ABCMeta):
    """
    An abstract time object that can be used for both Earth and Mars
    """
    __DT_TYPE__ = "AbstractDateTime"
    __LOCALE__ = None
    __DEFAULT_TIMEZONE__ = None
    __TIMEZONE_LOOKUP__ = {}
    NAMES = None
    EPOCH = (0, 1, 1)

    def __init__(self, tm_year=None, tm_mon=None, tm_mday=None, tm_hour=0, tm_min=0, tm_sec=0,
                 tm_tzone=0, tm_dst=None):
        """
        Set up with a date object. Inputs times are always UTC or MTC.
        Timezones and dst are then applied to that value.
        """
        tm_year = self.EPOCH[0] if tm_year is None else tm_year
        tm_mon = self.EPOCH[1] if tm_mon is None else tm_mon
        tm_mday = self.EPOCH[2] if tm_mday is None else tm_mday

        if tm_mon and not (0 < tm_mon <= self._months_in_year()):
            raise ValueError(
                f"Invalid month value: {tm_mon}. Month must be in [1 .. {self._months_in_year()}].")
        try:
            self.tm_tzone_offset = int(tm_tzone)
            if tm_tzone == 0:
                self.tm_tzone = self.__DEFAULT_TIMEZONE__
            else:
                self.tm_tzone = f"{self.__DEFAULT_TIMEZONE__}{self.fmt_timezone(self.tm_tzone_offset)}"
        except (ValueError, TypeError) as t_err:
            try:
                self.tm_tzone = tm_tzone
                self.tm_tzone_offset = self.__TIMEZONE_LOOKUP__[tm_tzone]
            except KeyError as k_err:
                raise ValueError(f"Unrecognised timezone '{tm_tzone}'")

        self.tm_dst = tm_dst  # Number or None
        try:
            self.tm_dst_offset = int(tm_dst)
        except (ValueError, TypeError) as err:
            self.tm_dst_offset = 0

        self.tm_offset = self.tm_tzone_offset + self.tm_dst_offset

        (self.tm_year, self.tm_mon, self.tm_mday,
         self.tm_hour, self.tm_min, self.tm_sec,) = self._normalise_date(
            tm_year, tm_mon, tm_mday,
            tm_hour, tm_min, tm_sec + self.tm_offset)

        #self.__validate_date()
        self.__tm_wday = None
        self.__tm_yday = None

    """
    def apply_offset(self, tm_offset):
        (self.tm_year, self.tm_mon, self.tm_mday,
         self.tm_hour, self.tm_min, self.tm_sec,) = self._normalise_date(
            self.tm_year, self.tm_mon, self.tm_mday,
            self.tm_hour, self.tm_min, self.tm_sec + tm_offset)
        self.tm_offset = tm_offset
        self.__tm_wday = None
        self.__tm_yday = None
    """

    def __repr__(self):
        tm_year, tm_mon, tm_mday = self.tm_year, self.tm_mon, self.tm_mday
        tm_hour, tm_min, tm_sec = self.tm_hour, self.tm_min, self.tm_sec
        tm_tzone, tm_dst = self.tm_tzone, self.tm_dst_offset

        params = ', '.join([
            f"{tm_year=}", f"{tm_mon=}", f"{tm_mday=}",
            f"{tm_hour=}", f"{tm_min=}", f"{tm_sec=}",
            f"{tm_tzone=}", f"{tm_dst=}"])

        return f"{self.__DT_TYPE__}({params})"

    def __str__(self):
        return ' '.join([
            f"{self.__DT_TYPE__}:",
            f"{self.tm_year}-{self.tm_mon:02d}-{self.tm_mday:02d}",
            f"{self.tm_hour:02d}:{self.tm_min:02d}:{self.tm_sec:02d}",
            f"{self.fmt_offset(self.tm_offset)}",
            f"({self.tm_tzone}"+(f"/{self.fmt_timezone(self.tm_dst_offset)}DST" if self.tm_dst_offset != 0 else '')+')'
        ])

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.epoch_tc_seconds == other.epoch_tc_seconds

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.epoch_tc_seconds < other.epoch_tc_seconds

    def __le__(self, other):
        return self.epoch_tc_seconds <= other.epoch_tc_seconds

    def __gt__(self, other):
        return self.epoch_tc_seconds > other.epoch_tc_seconds

    def __ge__(self, other):
        return self.epoch_tc_seconds >= other.epoch_tc_seconds

    def calculate_date_delta(self, b):
        if b.epoch_tc_days < self.epoch_tc_days:
            return calculate_date_delta(b, self)
        else:
            return calculate_date_delta(self, b)

    def fmt(self, pattern):
        formatter = StrFmtTime(pattern=pattern)
        return formatter.format_time(self)

    def fmt_date(self, sep='-'):
        return f"{self.tm_year}{sep}{self.tm_mon:02d}{sep}{self.tm_mday:02d}"

    def fmt_time(self):
        return f"{self.tm_hour:02d}:{self.tm_min:02d}"#:{self.tm_sec:02d}"

    def to_tuple(self):
        return DateTimeTup(self.tm_year, self.tm_mon, self.tm_mday,
                           self.tm_hour, self.tm_min, self.tm_sec,
                           #self.tm_wday, self.tm_yday, self.tm_offset
                            )

    def __validate_date(self):
        """
        Check the current date is valid.
        """
        mlens = self._days_in_months(year=self.tm_year)
        if not (0 < self.tm_mon <= len(mlens)):
            raise ValueError(f"Invalid month value: {self.tm_mon}. Month must be in [1 .. {len(mlens)}].")
        if not (0 < self.tm_mday <= mlens[self.tm_mon-1]):
            raise ValueError(f"Invalid day value: {self.tm_mday}. In month {self.tm_mon}, day must be in [1 .. {mlens[self.tm_mon-1]}].")

    @property
    def tm_wday(self):
        """Day of the week. 0 indexed"""
        if self.__tm_wday is None:
            self.__tm_wday = self._calc_weekday(self.tm_year, self.tm_mon, self.tm_mday)
        return self.__tm_wday

    @property
    def tm_yday(self):
        """Day of the year. 1 indexed."""
        if self.__tm_yday is None:
            self.__tm_yday = self._calc_yearday(self.tm_year, self.tm_mon, self.tm_mday)
        return self.__tm_yday

    @property
    #@abstractmethod
    def week_of_year(self):
        # Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
        # All days in a new year preceding the first Sunday are considered to be in week 0.
        raise NotImplementedError()

    @property
    def tm_wday_full(self):
        return self.NAMES['days']['full'][self.tm_wday]
        # return self.weekday_name(self.tm_wday, abrv=False)

    @property
    def tm_wday_abrv(self):
        return self.NAMES['days']['abrv'][self.tm_wday]
        # return self.weekday_name(self.tm_wday, abrv=True)

    @property
    def tm_mon_full(self):
        """Full month name"""
        return self.NAMES['months']['full'][self.tm_mon-1]
        # return self.month_name(self.tm_mon, abrv=False)

    @property
    def tm_mon_abrv(self):
        """Abbreviated month name"""
        return self.NAMES['months']['abrv'][self.tm_mon-1]

    @classmethod
    def weekday_name(cls, wday, abrv=False):
        return cls.NAMES['days']['abrv' if abrv else 'full'][wday]

    @classmethod
    def month_name(cls, mon, abrv=False):
        return cls.NAMES['months']['abrv' if abrv else 'full'][mon-1]

    @classmethod
    def fmt_offset(cls, offset):
        h = abs(offset) // 3600
        m = (abs(offset) // 60) % 60
        s = (abs(offset) % 60)
        sstr = '' if s == 0 else f".{s:02d}"
        return f"{'-' if offset < 0 else '+'}{h:02d}{m:02d}{sstr}"

    @classmethod
    def fmt_timezone(cls, offset):
        if offset == 0:
            return ''
        h = abs(offset) // 3600
        m = (abs(offset) // 60) % 60
        s = (abs(offset) % 60)
        return "".join([
            f"{'-' if offset < 0 else '+'}{h:d}",
            '' if (s == 0 and m == 0) else f":{m:02d}",
            '' if s == 0 else f".{s:02d}",
        ])

    @classmethod
    #@abstractmethod
    def _calc_weekday(cls, year, month, mday):
        raise NotImplementedError()

    @classmethod
    #@abstractmethod
    def _is_leap_year(cls, year):
        raise NotImplementedError()

    @classmethod
    #@abstractmethod
    def _days_in_months(cls, year=None):
        raise NotImplementedError()

    @classmethod
    def _days_in_month(cls, year, month):
        return cls._days_in_months(year)[month-1]

    @classmethod
    #@abstractmethod
    def _months_in_year(cls):
        raise NotImplementedError()

    @classmethod
    def _calc_yearday(cls, year, month, mday):
        """Calculate the day of the year.
        Total up the days of the previous months and add the day of the month."""
        return sum(cls._days_in_months(year)[:month-1]) + mday

    @classmethod
    def last_weekday_of_month(cls, year, month, weekday, hour=0, minute=0, second=0, as_dt=False):
        """
        Calculates the last instance of a given day of the week in a given month.
        """
        if as_dt:
            return cls(year, month, cls.last_weekday_of_month(year, month, weekday, as_dt=False),
                       hour, minute, second, tm_dst=0)

        mlens = cls._days_in_months(year=year)
        last_day = mlens[month-1]
        last_weekday = cls._calc_weekday(year=year, month=month, mday=last_day)
        if last_weekday == weekday:
            return last_day
        else:
            return last_day - (((7+last_weekday) - weekday) % 7)

    @classmethod
    def _normalise_date(cls, year, month, mday, hours, minutes, seconds):
        year, month, mday, hours, minutes, seconds = map(int, [year, month, mday, hours, minutes, seconds])
        # Normalise Seconds
        m, seconds = c_divmod(seconds, 60)
        minutes += m
        if (seconds < 0):
            seconds += 60
            minutes -= 1

        # Normalise Minutes
        h, minutes = c_divmod(minutes, 60)
        hours += h
        if (minutes < 0):
            minutes += 60
            hours -= 1

        # Normalise Hours
        d, hours = c_divmod(hours, 24)
        mday += d
        if (hours < 0):
            hours += 24
            mday -= 1

        # Normalise month/day
        month -= 1  # Make month zero based
        y, month = c_divmod(month, cls._months_in_year())
        year += y
        if (month < 0):
            month += cls._months_in_year()
            year -= 1
        month += 1  # back to one based

        # Normalise month/day
        while (mday < 1):
            month -= 1
            if (month == 0):
                month = cls._months_in_year()
                year -= 1
            mday += cls._days_in_month(year, month)

        while (mday > cls._days_in_month(year, month)):
            mday -= cls._days_in_month(year, month)
            month += 1
            if (month == cls._months_in_year()+1):
                month = 1
                year += 1
        return year, month, mday, hours, minutes, seconds

    #@abstractmethod
    def _intercalculate_year(self, year):
        raise NotImplementedError()

    @property
    def epoch_tc_seconds(self):
        """Seconds since the epoch. 0 indexed."""
        return (
                self.tm_sec
                + (self.tm_min * 60)
                + (self.tm_hour * 3600)
                + ((self._intercalculate_year(self.tm_year) + self.tm_yday - 1) * 86400)
                - (0 if self.tm_offset is None else self.tm_offset)
        )

    @property
    def epoch_tc_hours(self):
        """Hours since the epoch. 0 indexed """
        return (self.epoch_tc_seconds // 3600)

    @property
    def epoch_tc_days(self):
        """Day *of* the epoch. 1 indexed """
        return (self.epoch_tc_seconds // 86400) + 1


class EarthDateTime(AbstractDateTime):
    __DT_TYPE__ = 'EarthDateTime'
    __LOCALE__ = config.EARTH_DATETIME_LOCALE
    __DEFAULT_TIMEZONE__ = 'UTC'
    __TIMEZONE_LOOKUP__ = {'UTC': 0, "GMT": 0, "CET": 1*HOUR}
    NAMES = get_locale(__LOCALE__)
    EPOCH = (2000, 1, 1)

    def __init__(self, tm_year=None, tm_mon=None, tm_mday=None, tm_hour=0, tm_min=0, tm_sec=0,
                 tm_tzone=0, tm_dst=None):

        tm_year = self.EPOCH[0] if tm_year is None else tm_year
        tm_mon = self.EPOCH[1] if tm_mon is None else tm_mon
        tm_mday = self.EPOCH[2] if tm_mday is None else tm_mday
        if tm_dst is None:
            tm_dst = "BST"

        super().__init__(tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_tzone, tm_dst)
        # Default to BST calculation
        if self.tm_dst == "BST" and is_bst(self):
            self.tm_dst_offset = HOUR
            self.tm_offset = self.tm_tzone_offset + self.tm_dst_offset
            # Re-normalise the provided times
            (self.tm_year, self.tm_mon, self.tm_mday,
             self.tm_hour, self.tm_min, self.tm_sec,) = self._normalise_date(
                tm_year, tm_mon, tm_mday,
                tm_hour, tm_min, tm_sec+self.tm_offset)

    @classmethod
    def _calc_weekday(cls, year, month, mday):
        """Calculate the weekday from the date.
        The result is zero based with 0 = Monday.
        by Michael Keith and Tom Craver, 1990.
        """
        return (((23 * month // 9 + mday
                  + (year-1 if month < 3 else year-2)
                  + 4 + year // 4 - year // 100 + year // 400) +6) % 7)

    @property
    def week_of_year(self):
        # Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
        # All days in a new year preceding the first Sunday are considered to be in week 0.
        return ((self.tm_yday - (6 - self._calc_weekday(self.tm_year, 1, 1))) // 7) + 1

    @classmethod
    def _is_leap_year(cls, year=None):
        if year is None:
            return False
        return ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0)

    @classmethod
    def _days_in_months(cls, year=None):
        ly = 1 if cls._is_leap_year(year) else 0
        return [31, 28+ly, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    @classmethod
    def _months_in_year(cls):
        return 12

    @classmethod
    def _intercalculate_year(cls, year):
        return ((
            ((year - cls.EPOCH[0] + 3) // 4)  # add a day each 4 years starting with 2001
            - ((year - cls.EPOCH[0] + 99) // 100)  # subtract a day each 100 years starting with 2001
            + ((year - cls.EPOCH[0] + 399) // 400)  # add a day each 400 years starting with 2001
        ) + (year - cls.EPOCH[0]) * 365)

    def to_marstime(self, tm_tzone=0, tm_dst=None):
        return earthdatetime_2_marsdatetime(self, tm_tzone, tm_dst)

    @property
    def j2kdelta(self):
        return earthdatetime_2_j2kdelta_days(self)


class MarsDateTime(AbstractDateTime):
    __DT_TYPE__ = 'MarsDateTime'
    __LOCALE__ = config.MARS_DATETIME_LOCALE
    __DEFAULT_TIMEZONE__ = "MTC"
    __TIMEZONE_LOOKUP__ = {'MTC': 0}
    NAMES = get_locale(__LOCALE__)
    EPOCH = (0, 1, 1)

    @classmethod
    def _calc_weekday(cls, year, month, mday):
        """
        Calculate the weekday from the date.
        """
        return (mday+5) % 7

    @classmethod
    def _is_leap_year(cls, year=None):
        if year is None:
            return False
        if (year % 2 == 1) | ((year >= 10) & (year % 10 == 0)):
            if ((year >= 100) & (year % 100 == 0)) and not ((year >= 500) & (year % 500 == 0)):
                return False
            return True
        return False

    @classmethod
    def _days_in_months(cls, year=None):
        ly = 1 if cls._is_leap_year(year) else 0
        return [
            (27 if month % 6 == 0 else 28) + (ly if month == 24 else 0)
            for month in range(1, 25)]

    @classmethod
    def _months_in_year(cls):
        return 24

    @property
    def week_of_year(self):
        # Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
        return ((self.tm_mon - 1) * 4) + ((self.tm_mday // 7) + 1)

    @classmethod
    def _intercalculate_year(cls, year):
        """Calculate the number of days from year 0 to the start of the given year"""
        y = year-1
        return sum([(year // 2), int(y / 10), -int(y / 100), int(y / 1000)]) + (year * 668)


def earthdatetime_2_j2kdelta_days(earthdatetime):
    """As fractional days since the Julian date 2000-1-1 12:00 GMT"""
    return (earthdatetime.epoch_tc_seconds + (-43200 + 69.184)) / 86400


def j2kdelta_2_earthdatetime(j2kdelta):
    return EarthDateTime(tm_sec=(j2kdelta * 86400) - (-43200 + 69.184))


def earthdatetime_2_mars_standard_time(earthdatetime):
    """As MST"""
    j2kdelta = earthdatetime_2_j2kdelta_days(earthdatetime)
    return ((j2kdelta - 4.5) / 1.027491252) + 44796.0 - 0.00096  # 9626e-7


def earthdatetime_2_marsdatetime(earthdatetime, tm_tzone=0, tm_dst=None):
    mst = earthdatetime_2_mars_standard_time(earthdatetime)
    return mst_to_marsdatetime(mst, tm_tzone, tm_dst)


def fracdays_2_dhms(days):
    days, secs = c_divmod(days, 1)
    mins, secs = divmod(secs * 86400, 60)
    hours, mins = divmod(mins, 60)
    days, hours, mins, secs = map(int, (days, hours, mins, secs))
    return days, hours, mins, secs


def mst_to_marsdatetime(mst, tm_tzone=0, tm_dst=None):
    hour = mst % 1 * 24
    return MarsDateTime(
        tm_mday=int(mst) + 94129,
        tm_hour=int(hour),
        tm_min=int(hour * 60.0) % 60,
        tm_sec=int(hour * 36e2) % 60,
        tm_tzone=tm_tzone,
        tm_dst=tm_dst,
    )


def is_bst(earth_date_time):
    """
    Determine if the given date is during british summer time.
    The same rules apply for CET.
    Args:
        earth_date_time:

    Returns:

    """
    # Shortcut if we're outside of March/Oct
    if earth_date_time.tm_mon not in [3, 10]:
        return 3 < earth_date_time.tm_mon < 10
    year = earth_date_time.tm_year
    bst_start = EarthDateTime.last_weekday_of_month(
        year, 3, 6, 1, 0, earth_date_time.tm_tzone_offset, as_dt=True)
    bst_end = EarthDateTime.last_weekday_of_month(
        year, 10, 6, 1, 0, earth_date_time.tm_tzone_offset, as_dt=True)
    return bst_start <= earth_date_time < bst_end


def calculate_date_delta(a, b):
    y, m, d = b.tm_year - a.tm_year, b.tm_mon - a.tm_mon, b.tm_mday - a.tm_mday
    if d < 0:
        m -= 1
        if b.tm_mon - 1 >= 1:
            d = b._days_in_month(b.tm_year, b.tm_mon - 1) + d
        else:
            d = b._days_in_month(b.tm_year - 1, b._months_in_year()) + d
    if m < 0:
        m = b._months_in_year() + m
        y = y - 1
    return y, m, d


def next_date_occurrence(dt, target_mon, target_mday):
    """

    Args:
        dt: Starting date time
        target_mon: Target month
        target_mday: Target day of month

    Returns:
        AstroDate, the next occurrence of the
    """
    year = dt.tm_year
    if (dt.tm_mon > target_mon) or (dt.tm_mon == target_mon and dt.tm_mday > target_mday):
        year += 1
    return dt.__class__(year, target_mon, target_mday)
