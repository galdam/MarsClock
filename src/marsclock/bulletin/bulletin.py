from marsclock.astro import astrotime
from marsclock.helpers.math.random import MetaRand
from marsclock.bulletin import bulletinhelpers as helpers


class BulletinFetcher:
    def __init__(self, bdays_file, events_file, facts_file):
        self.dated_bulletin_files = [bdays_file, events_file]
        self.dated_bulletin_formatters = [
            (helpers.format_earth_bday, helpers.format_mars_bday),
            (helpers.format_earth_event, helpers.format_mars_event),
        ]
        self.facts_file = facts_file
        self.n_facts = helpers.count_lines(self.facts_file)

    def collect_dated_bulletins(self, earth_date_now, mars_date_now):
        messages = []
        etd = earth_date_now.fmt_date().split('-',1)[-1]
        mtd = mars_date_now.fmt_date().split('-',1)[-1]

        for msg_file, formatters in zip(self.dated_bulletin_files, self.dated_bulletin_formatters):
            with open(msg_file) as fh:
                for l in fh:
                    l = l.strip('\n')
                    if not l or l.startswith('#'):
                        continue
                    try:
                        earth_event_date, mars_event_date, msg = l.split('\t', 2)
                    except Exception as err:
                        print(l)
                        raise err
                    unpacked = helpers.unpack_dates(earth_event_date, mars_event_date)
                    if mtd == unpacked[1][1]:
                        messages.append(formatters[1](unpacked, earth_date_now, mars_date_now, msg))
                        continue
                    if etd == unpacked[0][1]:
                        messages.append(formatters[0](unpacked, earth_date_now, mars_date_now, msg))
                        continue
        return messages

    def collect_fact_bulletins(self, n):
        return [
            helpers.extract_line(self.facts_file, line_num)
            for line_num in MetaRand.random_number_picker(self.n_facts, n)]


