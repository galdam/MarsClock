
from marsclock.bulletin.bulletin import BulletinFetcher
from marsclock.widget.constellation import ConstellationWidget
from marsclock.mathutils import MetaRand
from marsclock.widget.moonphase import MoonPhaseWidget
from marsclock.astro.astrotime import next_date_occurrence
import re

facts_file = 'resources/content/facts.tsv'
bdays_file = 'resources/content/birthdays.tsv'
events_file = 'resources/content/events.tsv'

CK = 0
CW = 1


class BulletinWidget:
    def __init__(self, display, size, position, min_bulletins=2):
        self.display = display
        self.epd = display.epd
        self.bulletin_fetcher = BulletinFetcher(bdays_file, events_file, facts_file)
        self.constellation_widget = ConstellationWidget(self.display, 0, position=(15, 85))
        self.min_bulletins = min_bulletins
        self.char_width = 8
        self.char_height = 8
        self.line_height = 10

        self.line_length = (400-(16*2)) // self.char_width
        self.message_formatter = setup_message_formatter(self.line_length, a_indent_str='', b_indent_str='')
        self.bulletins = None

    def draw(self):
        self.bulletins = self.prepare_bulletins()
        if self.bulletins:
            self.draw_bulletins(self.bulletins)
        else:
            self.constellation_widget.draw()

    def prepare_bulletins(self):
        # Load dated bulletins
        bulletins = self.bulletin_fetcher.collect_dated_bulletins(
            self.display.earth_time, self.display.mars_time)

        # If there are no dated bulletins, consider displaying constellations
        # Always consume a rand digit here to keep the clocks in sync
        show_constellations = MetaRand.rand_int(20) == 0
        if not bulletins and show_constellations:
            return

        if len(bulletins) < self.min_bulletins:
            bulletins.extend(
                self.bulletin_fetcher.collect_fact_bulletins(
                    self.min_bulletins - len(bulletins)))
        return bulletins

    def draw_bulletins(self, bulletins):
        bulletins = [EmbeddedWidget.extract_embedded_widget(msg) for msg in bulletins]
        bulletins = [[self.message_formatter(msg), w] for msg, w in bulletins]
        n_lines = sum(len(b[0]) for b in bulletins)
        n_para = len(bulletins)
        y_start = 82
        ltext = 16
        height = (300 - 10) - y_start

        wspace = (height - (n_lines * self.line_height)) // (n_para * 2)
        pos = y_start
        for b_num, (bulletin, embedded_widget) in enumerate(bulletins):
            pos += wspace
            for line in bulletin:
                widget_loc = None
                if embedded_widget:
                    line, widget_loc = EmbeddedWidget.widget_loc(line)
                self.epd.text(line, ltext, pos, CK)
                if widget_loc:
                    self.apply_widget(x=((widget_loc-1)*self.char_width)+ltext,
                                      y=pos,
                                      w=embedded_widget)
                pos += self.line_height
            pos += wspace
            if b_num < len(bulletins) -1:
                self.epd.line(200 - 30, pos, 200 + 30, pos, CK)

    def apply_widget(self, x, y, w):
        widget, params = w.split(':', 1)
        if widget == 'MP':
            __, target_mon, target_mday = params.split('-')
            dt = next_date_occurrence(self.display.earth_time, int(target_mon), int(target_mday))
            MoonPhaseWidget(self.display, self.char_width, (x, y)).draw_moon_by_date(dt)
        else:
            raise NotImplementedError(f"No widget for: {widget}")


class EmbeddedWidget:
    widget_pattern = re.compile(r'\+[\w:-]+\+')
    widget_placeholder_pattern = re.compile(r'\++')

    widget_placeholder_sizes = {
        'MP': 1,
    }

    @classmethod
    def extract_embedded_widget(cls, msg):
        bulletin_widget = None
        matched = cls.widget_pattern.search(msg)
        if matched:
            bulletin_widget = matched.group(0).strip('+')
            msg = ''.join(
                [msg[:matched.span()[0]],]
                + ['+'] * cls.widget_placeholder_sizes[bulletin_widget.split(':')[0]]
                + [msg[matched.span()[1]:]]
            )

        return msg, bulletin_widget

    @classmethod
    def widget_loc(cls, msg):
        matched = cls.widget_placeholder_pattern.search(msg)
        if not matched:
            return msg, None
        msg = ''.join(
            [msg[:matched.span()[0]]]
            + [' ']*(matched.span()[1]-matched.span()[0])
            + [msg[matched.span()[1]:]]
        )
        return msg, matched.span()[1]


def setup_message_formatter(line_length, a_indent_str='', b_indent_str=''):
    def __message_formatter(message):
        nonlocal line_length, a_indent_str, b_indent_str

        formatted_msg = []
        paragraphs = message.split('|')
        for paragraph in paragraphs:
            # Set and trim the paragraph alignment signifier
            if paragraph[0] in ['^', '>', '<']:
                alignment = paragraph[0]
                paragraph = paragraph[1:]
            else:
                alignment = '<'

            words = paragraph.split(' ')
            # Add an indent to left aligned paragraph start
            a_indent = a_indent_str if alignment == '<' else ''
            b_indent = b_indent_str if alignment == '<' else ''

            lines = [''.join([a_indent, words[0]]), ]
            for word in words[1:]:
                if (len(lines[-1]) + len(word) + 1) <= line_length:
                    lines[-1] = ' '.join([lines[-1], word])
                else:
                    lines.append(''.join([b_indent, word]))
            lines = [f'{line:{alignment}{line_length}}' for line in lines]
            formatted_msg.extend(lines)
        return formatted_msg
    return __message_formatter

