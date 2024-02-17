import random
from marsclock import marstime

facts_file = '../resources/content/facts.tsv'
birthdays_file = '../resources/content/birthdays.tsv'
events_file = '../resources/content/events.tsv'


line_length = (400//8)-4


def select_messages(earth_date_now, mars_date_now):
    """"""
    #earth_date_now = make_datetime_tup(*map(int, edt.split('-')))
    #mars_date_now = marstime.MarsCal.from_earthtime(earth_date_now)
    msgs = get_birthdays(earth_date_now, mars_date_now) + get_events(earth_date_now, mars_date_now)
    if 0 < len(msgs) < 2:
        msgs.append(get_random_fact(8))
    if not msgs:
        if random.randint(0, 10) == 0:
            return None
        msgs = [get_random_fact()]
        if len(format_message(msgs[0])) <= 8:
            msgs.append(get_random_fact(8))
    return msgs


def format_message(message):
    paragraph = []
    sentances = message.split('|')
    for sentance in sentances:
        if sentance[0] in ['^','>','<']:
            a = sentance[0]
            sentance = sentance[1:]
        else:
            a = '<'
        indent = '  ' if a == '<' else ''
        words = sentance.split(' ')
        lines = [words[0], ] 
        for word in words[1:]:
            if (len(lines[-1]) + len(word) + 1) <= line_length:
                lines[-1] = ' '.join([lines[-1], word])
            else:
                lines.append(indent + word)
        lines = [f'{line:{a}{line_length}}' for line in lines]
        paragraph.extend(lines)
    return paragraph

def check_date(date, current_mon_day):
    if not date:
        return 
    year, mon_day = date.split('-', 1)
    if mon_day == current_mon_day:
        return year, mon_day

def get_mst(year, month, day):
    return marstime.MarsTime.from_earthtime(marstime.make_struct_time(year, month, day))

def get_marsdate(year, month, day):
    return marstime.MarsCal.from_earthtime(marstime.make_struct_time(year, month, day))


    

### Facts
def count_facts():
    with open(facts_file, 'r') as fh:
        i = 0
        for i, __ in enumerate(fh):
            pass
    return i

facts_length = count_facts()

def get_random_fact(max_line=None):
    #if facts_length is None:
    #    facts_length = count_facts()
    target = random.randint(0, facts_length)
    with open(facts_file, 'r') as fh:
        for i, l in enumerate(fh):
            if i == target:
                l = l.strip()
                break  
        else:
            l = 'Space, the final frontier...'
    if max_line is not None and len(format_message(l)) > max_line:
        l = get_random_fact(max_line)
    return l
            

### Birthdays

def get_birthdays(earth_date_now, mars_date_now):
    earth_mon_day = f'{earth_date_now.tm_mon:02d}-{earth_date_now.tm_mday:02d}'
    mars_mon_day = f'{mars_date_now.tm_mon:02d}-{mars_date_now.tm_mday:02d}'
    
    messages = []
    with open(birthdays_file, 'r') as fh:
        for l in fh:
            name, earth_date, mars_date = l.strip('\n').split('\t')
            r = check_date(mars_date, mars_mon_day)
            if r:
                messages.append(format_mars_birthday_message(name, earth_date, mars_date_now))
                continue
            r = check_date(earth_date, earth_mon_day)
            if r:
                messages.append(format_earth_birthday_message(name, earth_date, mars_date_now))
    return messages


def format_earth_birthday_message(name, earth_bday, mars_date_now):
    year, month, day = map(int, earth_bday.split('-'))
    mars_bday = get_marsdate(year, month, day)
    years_delta, months_delta, sols_delta = mars_timedelta(mars_bday, mars_date_now)
    month_name, weekday = marstime.MarsCal.date_names(mars_bday)
    months_message = '' if months_delta == 0 else f" and {months_delta} month{'' if months_delta == 1 else 's'}"
    return ' '.join([f"Today is {name}'s birthday. On Mars, the date was {mars_bday.tm_mday} {month_name}, {mars_bday.tm_year}.",
                     f"In Mars time, {name} would be {years_delta} years{months_message} old."])

def format_mars_birthday_message(name, earth_bday, mars_date_now):
    year, month, day = map(int, earth_bday.split('-'))
    mars_bday = get_marsdate(year, month, day)
    years_delta, months_delta, sols_delta = mars_timedelta(mars_bday, mars_date_now)
    return f"If born on Mars, today would be {name}'s birthday. In Mars time, {name} would be {years_delta} years old."


#### Historical events

def get_events(earth_date_now, mars_date_now):
    earth_mon_day = f'{earth_date_now.tm_mon:02d}-{earth_date_now.tm_mday:02d}'
    mars_mon_day = f'{mars_date_now.tm_mon:02d}-{mars_date_now.tm_mday:02d}'
    
    messages = []
    with open(events_file, 'r') as fh:
        for l in fh:
            earth_date, mars_date, msg = l.strip('\n').split('\t')
            r = check_date(mars_date, mars_mon_day)
            if r:
                messages.append(format_mars_event(r[0], earth_date, msg))
                continue
            r = check_date(earth_date, earth_mon_day)
            if r:
                messages.append(format_earth_event(r[0], msg))
    return messages

def format_earth_event(year, msg):
    if year:
        return f"This day in {year}, {msg}"
    return msg
    
def format_mars_event(year, earth_date, msg):
    if year:
        return f"This sol in {year} ({earth_date.replace('-', '/')}), {msg}"
    return msg

