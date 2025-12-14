import re

_FMT_LOOKUP = {k: ':02d' for k in ['d', 'm', 'H', 'I', 'M', 'S']}
_FMT_LOOKUP.update({'j': ':03d'})


class StrFmtTime:
    _FMT_LOOKUP = _FMT_LOOKUP
    _RE_PCT = re.compile('%-?[A-z]')

    def __init__(self, pattern):
        self.format_attributes = []
        self.pattern = pattern
        self.formatter = self._compile_formatter(pattern)

    def format_time(self, dt):
        dta = DateTimeAttributes(dt)
        return self.formatter.format(**{p: getattr(dta, p) for p in self.format_attributes})

    def _compile_formatter(self, pattern):
        formatter = pattern
        while True:
            matched = self._RE_PCT.search(formatter)
            if not matched:
                break
            m = matched.group(0)
            # If the - is included, the lookup fails and no leading digits are used.
            f = ''.join(['{', m[-1], self._FMT_LOOKUP.get(m[1:], ''), '}'])
            self.format_attributes.append(m[-1])
            formatter = formatter.replace(m, f)
        formatter = formatter.replace('%%', '%')
        return formatter


class DateTimeAttributes:
    """
    A wrapper class that takes an AstroDateTime and exposes the strftime directives as attributes.

    a: Locale's three letter abbreviated weekday name
    A: Locale's full weekday name
    b: Locale's three letter abbreviated month name
    B: Locale's full month name
    d: Day of the month as a decimal number [01,31]
    H: Hour (24-hour clock) as a decimal number [00,23]
    I: Hour (12-hour clock) as a decimal number [01,12]
    j: Day of the year as a decimal number [001,366]
    m: Month as a decimal number [01,12]
    M: Minute as a decimal number [00,59]
    p: Locale's equivalent of either AM or PM
    S: Second as a decimal number [00,61]
    z: Time zone offset indicating a positive or negative time difference
        from UTC/GMT of the form +HHMM or -HHMM, where H represents decimal
        hour digits and M represents decimal minute digits [-23:59, +23:59]
    w: Weekday as a decimal number [0(Sunday),6]
    U: Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
        All days in a new year preceding the first Sunday are considered to be in week 0.
    Y: Year with century as a decimal number
    x: Locale's appropriate date representation (Y/m/d)
    X: Locale's appropriate time representation (H:M)
    """
    def __init__(self, dt):
        self.dt = dt

    @property
    def a(self):
        # Locale's three letter abbreviated weekday name
        return self.dt.weekday_name(self.dt.tm_wday, abrv=True)

    @property
    def A(self):
        # Locale's full weekday name
        return self.dt.weekday_name(self.dt.tm_wday, abrv=False)

    @property
    def b(self):
        # Locale's three letter abbreviated month name
        return self.dt.month_name(self.dt.tm_mon, abrv=True)

    @property
    def B(self):
        # Locale's full month name
        return self.dt.month_name(self.dt.tm_mon, abrv=False)

    @property
    def d(self):
        # Day of the month as a decimal number [01,31]
        return self.dt.tm_mday

    @property
    def H(self):
        # Hour (24-hour clock) as a decimal number [00,23]
        return self.dt.tm_hour

    @property
    def I(self):
        # Hour (12-hour clock) as a decimal number [01,12]
        return 12 if self.dt.tm_hour in [0, 12] else self.dt.tm_hour % 12

    @property
    def j(self):
        # Day of the year as a decimal number [001,366]
        return self.dt.tm_yday

    @property
    def m(self):
        # Month as a decimal number [01,12]
        return self.dt.tm_mon

    @property
    def M(self):
        # Minute as a decimal number [00,59]
        return self.dt.tm_min

    @property
    def p(self):
        # Locale's equivalent of either AM or PM
        return 'AM' if self.dt.tm_hour < 13 else 'PM'

    @property
    def S(self):
        # Second as a decimal number [00,61]
        return self.dt.tm_sec

    @property
    def z(self):
        # Time zone offset indicating a positive or negative time difference from UTC/GMT of the form +HHMM or -HHMM,
        # where H represents decimal hour digits and M represents decimal minute digits [-23:59, +23:59]
        return self.dt.fmt_offset(self.dt.tm_offset)

    @property
    def w(self):
        # Weekday as a decimal number [0(Sunday),6]
        return (self.dt.tm_wday + 1) % 7

    @property
    def U(self):
        # Week number of the year (Sunday as the first day of the week) as a decimal number [00,53].
        # All days in a new year preceding the first Sunday are considered to be in week 0.
        return self.dt.week_of_year

    @property
    def Y(self):
        # Year with century as a decimal number
        return self.dt.tm_year

    @property
    def x(self):
        # Locale's appropriate date representation
        return f'{self.dt.tm_year}/{self.dt.tm_mon:02d}/{self.dt.tm_mday:02d}'

    @property
    def X(self):
        # Locale's appropriate time representation
        return f'{self.dt.tm_hour:02d}:{self.dt.tm_min:02d}'
