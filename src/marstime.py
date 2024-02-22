import time
import math
from collections import namedtuple


MARS_MONTHS = 'Darian'
MARS_DAYS = 'Darian'
EARTH_MONTHS = 'Gregorian'
EARTH_DAYS = 'English'

MONTHS = {
    'Darian': {
        1: 'Sagittarius', 2: 'Dhanus', 3: 'Capricornus', 4: 'Makara', 5: 'Aquarius', 6: 'Kumbha',
        7: 'Pisces', 8: 'Mina', 9: 'Aries', 10: 'Mesha', 11: 'Taurus', 12: 'Rishabha',
        13: 'Gemini', 14: 'Mithuna', 15: 'Cancer', 16: 'Karka', 17: 'Leo', 18: 'Simha',
        19: 'Virgo', 20: 'Kanya', 21: 'Libra', 22: 'Tula', 23: 'Scorpius', 24: 'Vrishika'},
    'Utopian': {
        1: 'Phoenix', 2: 'Cetus', 3: 'Dorado', 4: 'Lepus', 5: 'Columbia', 6: 'Monoceros',
        7: 'Volans', 8: 'Lynx', 9: 'Camelopardalis', 10: 'Chamaeleon', 11: 'Hydra', 12: 'Corvus',
        13: 'Centaurus', 14: 'Draco', 15: 'Lupus', 16: 'Apus', 17: 'Pavo', 18: 'Aquila',
        19: 'Vulpecula', 20: 'Cygnus', 21: 'Delphinus', 22: 'Grus', 23: 'Pegasus', 24: 'Tucana'},
    'Chinese': {
        1: 'Chunfen', 2: 'Qingming', 3: 'Guyu', 4: 'Lixia', 5: 'Xiaoman', 6: 'Mangzhong',
        7: 'Xiazhi', 8: 'Xiaoshu', 9: 'Dashu', 10: 'Liqiu', 11: 'Chushu', 12: 'Bailu',
        13: 'Qiufen', 14: 'Hanlu', 15: 'Shuangjiang', 16: 'Lidong', 17: 'Xiaoxue', 18: 'Daxue',
        19: 'Dongzhi', 20: 'Xiaohan', 21: 'Dahan', 22: 'Lichun', 23: 'Yushui', 24: 'Jingzhe'},
    'Gregorian': {
        1: 'January', 2:'February', 3:'March', 4:'April', 5:'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11:'November', 12: 'December'},
    }
DAYS = {
    'Darian': {
        0: 'Saturni', 1: 'Solis', 2: 'Lunae', 3: 'Martis', 4: 'Mercurii', 5: 'Jovis', 6: 'Veneris',},
    'English': {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday',},
}


DateTimeTup = namedtuple(
    'DateTimeTup',
    ('tm_year', 'tm_mon', 'tm_mday', 'tm_hour', 'tm_min', 'tm_sec', 'tm_wday', 'tm_yday'))

def compare_datetimes(time_a, time_b):
    return [a == b for a, b in zip(time_a, time_b)]


def make_struct_time(tm_year, tm_mon, tm_mday, tm_hour=0, tm_min=0, tm_sec=0, *args):
    #return time.struct_time((tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, 0, 1, -1))
    return (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, 0, 1, -1)


#def make_datetime_tup(*args):
#    return DateTimeTup(make_struct_time(*args))

def make_datetime_tup(*args, **kwargs):
    return DateTimeTup(*make_struct_time(*args, **kwargs)[:8])

def format_date_tup(dt):
    return f'{dt.tm_year}-{dt.tm_mon:02d}-{dt.tm_mday:02d}'

class EarthCal:
    @staticmethod
    def now():
        return time.gmtime()
    
    @staticmethod
    def print_datetime(earth_time):
        return print_datetime(earth_time, EarthCal.date_names(earth_time))
    
    @staticmethod
    def date_names(datetimetup):
        month = datetimetup.tm_mon
        weekday = datetimetup.tm_wday
        return MONTHS[EARTH_MONTHS][month], DAYS[EARTH_DAYS][weekday]


class MarsCal:
    @staticmethod
    def now():
        return MarsCal.from_earthtime(EarthCal.now())

    @staticmethod
    def print_datetime(mars_time):
        return print_datetime(mars_time, MarsCal.date_names(mars_time))

    @staticmethod
    def timedelta(date_a, date_b):
        years = date_b.tm_year - date_a.tm_year
        sols = date_b.tm_yday - date_a.tm_yday 
        if sols < 0:
            sols += 668
            years -= 1
        return years, sols // 28, sols % 28

    @staticmethod
    def from_earthtime(datetimetup):
        """Turn an earth time tuple into a mars time tuple"""
        # Earth time to unix epoch to julian 2000 delta
        ##return mst_2_marstime(earthtime_2_mst(datetimetup))
        mst = MarsTime.from_earthtime(datetimetup)
        return MarsCal.from_marstime(mst)

    @staticmethod
    def date_names(datetimetup):
        month = datetimetup.tm_mon
        weekday = datetimetup.tm_wday
        return MONTHS[MARS_MONTHS][month], DAYS[MARS_DAYS][weekday]

    @staticmethod
    def from_marstime(mst):
        sol_day, hour, minute, second = mst
        year, yearday = MarsCal.solday_2_year(sol_day)
        month, mday = MarsCal.dayofyear_2_month(year, yearday)
        weekday = mday % 7
        return DateTimeTup(year, month, mday, hour, minute, second, weekday, yearday)

    @staticmethod
    def is_leap_year(year):
        """Determine if it's a leap year on mars"""
        if (year % 2 == 1) | (year % 10 == 0):
            if (year % 100 == 0) and not (year % 500 == 0):
                return False
            return True
        return False

    @staticmethod
    def days_in_month(month, year=1):
        """Mars months have 28 days, except for every 6th month which has 27
        The last month gets an extra day in a leap year"""
        if not (1 <= month <= 24):
            raise ValueError('Month out of range')
        d = 27 if month % 6 == 0 else 28
        if (month == 24) and MarsCal.is_leap_year(year):
            d += 1
        return d

    @staticmethod
    def year_length(year):
        """668 or 669 in a leap year"""
        return 668 + int(MarsCal.is_leap_year(year))

    @staticmethod
    def intercalculate_year(year):
        """Calculate the number of days from year 0 to the start of the given year"""
        year = year -1
        return sum([((year+1)//2), (year//10), -(year//100), (year//500)])

    @staticmethod
    def intercalculate_days(month, year):
        """Calculate the number of days to the start of this month"""
        return sum([MarsCal.days_in_month(i, year) for i in range(1, month)])

    @staticmethod
    def year_start(year):
        """The sol date that this year started"""
        mod = 94128
        return int(((668 * year) + MarsCal.intercalculate_year(year)) - mod)

    @staticmethod
    def solday_2_year(sol_day):
        """For a given sol day calculate the mars year
        There should be a better way but for now, take an educated guess,
         if it's wrong, adjust as needed."""
        year = int((sol_day + 94128) // 668.5)
        for __ in range(10):
            st, en = MarsCal.year_start(year), MarsCal.year_start(year+1)
            #print(year, st, '<=', sol_day, '<', en, st <= sol_day < en)
            if sol_day < st:
                year -= 1
                continue
            if sol_day >= en:
                year += 1
                continue
            break
        else:
            raise ValueError('Error estimating year')
        return year, (sol_day - MarsCal.year_start(year)) + 1

    @staticmethod
    def dayofyear_2_month(year, days):
        """Convert day of year, to month and day"""
        year_total = 0
        for month in range(1, 25):
            dim = MarsCal.days_in_month(month, year=year)
            if year_total + dim >= days:
                break
            year_total += dim
        return month, days-year_total


class MarsTime:
    J2K_epoch_start = time.mktime((2000, 1, 1, 12, 0, 0, 0, 0, 0))
    J2K_epoch_start = J2K_epoch_start + 388736

    @staticmethod
    def now():
        return MarsTime.from_earthtime(EarthCal.now())

    @staticmethod
    def j2kdelta_2_mst(j2kdelta):
        # Convert a j2k delta into MST
        mst = j2kdelta / 1.0274912517 + 44796.0 - 9626e-7
        hour = mst % 1 * 24
        return (
            int(mst),
            int(hour),
            int(hour * 60.0) % 60,
            int(hour * 36e2) % 60,
            #int(hour * 36e8) % 1000000, # Disable microsecond precision
        )

    @staticmethod
    def from_earthtime(tm):
        """Get the mst: sol day, hour, minute, seconds
        If sol day hasn't changed, no need to recalculate the marstime"""
        tm = make_struct_time(*tm)
        return MarsTime.from_earthseconds(time.mktime(tm))
        
    @staticmethod   
    def from_earthseconds(seconds_since_unix_epoch):
        """Get the mst: sol day, hour, minute, seconds
        If sol day hasn't changed, no need to recalculate the marstime"""
        j2kdelta = (seconds_since_unix_epoch - MarsTime.J2K_epoch_start) / 86400
        mst = MarsTime.j2kdelta_2_mst(j2kdelta)
        return mst

def print_datetime(dt, cal_names):
    month_name, day_name = cal_names
    print(dt)
    return [
        f'{day_name}',
        f'{dt.tm_mday} {month_name}',
        # f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}:{dt.tm_sec:0>2d}',
        f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}',#:{dt.tm_sec:0>2d}',
        f'{dt.tm_year}/{dt.tm_mon:0>2d}/{dt.tm_mday:0>2d}',
    ]


def time_to_period(hour):
    abrv = 'am' if hour < 12 else 'pm'
    hr = hour % 12
    hr = 12 if hr == 0 else hr
    return f'{hr}{abrv}'


if __name__ == '__main__':
    #earth_time = DateTimeTup(tm_year=2023, tm_mon=12, tm_mday=14, tm_hour=21, tm_min=54, tm_sec=49, tm_wday=3, tm_yday=0)

    #earth_time = DateTimeTup(tm_year=2020, tm_mon=12, tm_mday=15, tm_hour=21, tm_min=29, tm_sec=23, tm_wday=3, tm_yday=0)

    #DateTimeTup(tm_year=220, tm_mon=13, tm_mday=11, tm_hour=22, tm_min=41, tm_sec=15, tm_wday=4, tm_yday=345)
    #DateTimeTup(tm_year=2023, tm_mon=12, tm_mday=14, tm_hour=21, tm_min=29, tm_sec=27, tm_wday=3, tm_yday=0)
    #DateTimeTup(tm_year=220, tm_mon=13, tm_mday=11, tm_hour=22, tm_min=41, tm_sec=15, tm_wday=4, tm_yday=345)
    #DateTimeTup(tm_year=2023, tm_mon=12, tm_mday=14, tm_hour=21, tm_min=29, tm_sec=32, tm_wday=3, tm_yday=0)
    #DateTimeTup(tm_year=220, tm_mon=13, tm_mday=11, tm_hour=22, tm_min=41, tm_sec=15, tm_wday=4, tm_yday=345)
    #et = earth_time
    earth_time = (2020, 12, 14, 22, 9, 10, 3, 348)
    mst = MarsTime.from_earthtime(earth_time)
    tm = make_struct_time(*earth_time)
    print(time.mktime(tm) )
    print(mst)
    
    earth_time = (2020, 12, 14, 22, 9, 20, 3, 348)
    mst = MarsTime.from_earthtime(earth_time)
    tm = make_struct_time(*earth_time)
    print(time.mktime(tm) )
    print(mst)
    
    earth_time = (2020, 12, 14, 22, 9, 30, 3, 348)
    mst = MarsTime.from_earthtime(earth_time)
    tm = make_struct_time(*earth_time)
    print(time.mktime(tm) )
    print(mst)
    
    while True:
        earth_time = time.gmtime()
        mst = MarsTime.from_earthtime(earth_time)
        mars_time = MarsCal.from_earthtime(earth_time)
        print(earth_time)
        print(mst)
        print(mars_time)
        time.sleep(5)
        break
    #from ds3231_gen import DS3231
    #ds3231 = DS3231()
    
    #while True:
    #    earth_time = DateTimeTup(*ds3231.get_time())
    #    mars_time = MarsCal.from_earthtime(earth_time)
    #    print(mars_time)
    #    time.sleep(3)
    #earth_time = time.gmtime()
    #mars_time = MarsCal.from_earthtime(earth_time)
    #earth_dt = print_datetime(earth_time, EarthCal.date_names(earth_time))
    #mars_dt = print_datetime(mars_time, MarsCal.date_names(mars_time))
    #print('\n'.join(earth_dt))
    #print('\n'.join(mars_dt))
