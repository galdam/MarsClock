import marstime


def get_birthday_record(name, year, month, day):
    earth_dt = marstime.make_datetime_tup(year, month, day)
    mars_dt = marstime.MarsCal.from_earthtime(earth_dt)
    return name, marstime.format_date_tup(earth_dt), marstime.format_date_tup(mars_dt)
    

if __name__ == '__main__':
    birthdays = [
        ('Gabe', 1990, 1, 4),
        ('Curt', 1991, 7, 9,),
        ('Alan', 1981, 3, 31),
        ('Mike', 1977, 9, 29),
        ('Harriet', 1989, 4, 13),
        ('Liv', 1992, 7, 15 ),
        ('Ma', 1957, 3, 21),
        ('Pa', 1955, 11, 7),
    ]
    with open('data/birthdays.tsv', 'w') as fh:
        fh.write('\n'.join(['\t'.join(get_birthday_record(*b)) for b in birthdays]))
    