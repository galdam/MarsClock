# from marsclock import marstime
from marsclock.astro import astrotime


def get_birthday_record(year, month, mday):
    """
    Take the earth date and convert it to a mars time.
    """
    earth_dt = astrotime.EarthDateTime(year, month, mday)
    mars_dt = earth_dt.to_marstime()
    return [earth_dt.fmt_date(), mars_dt.fmt_date()]


def add_birthdays():
    """

    """
    input_birthdays_path = '../birthdays.tsv'
    root = __file__.rsplit('/', 1)[0]
    resource_birthdays_path = f"{root}/../resources/content/birthdays.tsv"
    try:
        with open(input_birthdays_path, 'r') as fh_in, open(resource_birthdays_path, 'w') as fh_out:
            for l in fh_in:
                l = l.strip('\n')
                if not l:
                    continue
                birthday, name = l.split('\t')
                year, month, mday = [int(v) for v in birthday.split('-')]
                fh_out.write('\t'.join(get_birthday_record(year, month, mday) + [name]))
                fh_out.write('\n')
    except OSError as err:
        print(err)
        return


if __name__ == '__main__':
    add_birthdays()
