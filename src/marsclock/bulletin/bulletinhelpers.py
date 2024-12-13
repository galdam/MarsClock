from marsclock.astro import astrotime


def unpack_dates(earth_date, mars_date):
    (earth_year, earth_md) = earth_date.split('-', 1) if earth_date else ('', '',)
    (mars_year, mars_md) = mars_date.split('-', 1) if mars_date else ('', '')
    return (earth_year, earth_md, earth_date), (mars_year, mars_md, mars_date)


def format_earth_bday(unpacked, earth_date_now, mars_date_now, name):
    mars_bday = astrotime.MarsDateTime(*map(int, unpacked[1][2].split('-')))
    years_delta, months_delta, d = mars_bday.calculate_date_delta(mars_date_now)
    months_delta_message = '' if months_delta == 0 else f" and {months_delta} month{'' if months_delta == 1 else 's'}"
    return ' '.join([f"Today is {name}'s birthday. On Mars, the date was {mars_bday.tm_mday} {mars_bday.tm_mon_full}, {mars_bday.tm_year}.",
                     f"In Mars time, {name} would be {years_delta} years{months_delta_message} old."])


def format_mars_bday(unpacked, earth_date_now, mars_date_now, name):
    mars_bday = astrotime.MarsDateTime(*map(int, unpacked[1][2].split('-')))
    years_delta, months_delta, d = mars_bday.calculate_date_delta(mars_date_now)
    return f"If born on Mars, today would be {name}'s birthday. In Mars time, {name} would be {years_delta} years old."


def format_earth_event(unpacked, earth_date_now, mars_date_now, msg):
    earth_year = unpacked[0][0]
    if earth_year:
        return f"This day in {earth_year}, {msg}"
    return msg


def format_mars_event(unpacked, earth_date_now, mars_date_now, msg):
    mars_year = unpacked[1][0]
    if mars_year:
        return f"This sol in {mars_year} ({unpacked[0][2].replace('-', '/')}), {msg}"
    return msg


def extract_line(file, line_num):
    with open(file, 'r') as fh:
        for i, l in enumerate(fh):
            if i == line_num:
                return l.strip('\n')


def count_lines(file):
    with open(file, 'r') as fh:
        for i, l in enumerate(fh):
            pass
        return i

