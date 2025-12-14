import re

from marsclock.bulletin.bulletin import BulletinFetcher
from marsclock.widget.asterism import AsterismWidget
from marsclock.widget.moonphase import MoonPhaseWidget
from marsclock.widget.symbol import SymbolWidget
from marsclock.helpers.math.random import MetaRand
from marsclock.astro.astrotime import next_date_occurrence
from marsclock.widget.abswidget import AbsWidget

from marsclock.config import RESOURCE_PATH

#resource_dir=os.path.join(os.path.dirname(__file__), '..', '..' , 'resources', 'content')

facts_file = '/'.join([RESOURCE_PATH, 'content','facts.tsv'])
bdays_file = '/'.join([RESOURCE_PATH, 'content', 'birthdays.tsv'])
events_file = '/'.join([RESOURCE_PATH, 'content', 'events.tsv'])


class BulletinWidget(AbsWidget):

    @property
    def minimum_size(self) -> tuple[int, int]:
        """
        Returns: (int, int), width, height,
        """
        return 400,200

    def __init__(self, hardware, position, size, min_bulletins=2):
        super().__init__(hardware, position, size)
        self.colors.add_color('BG', 'WHITE')
        self.colors.add_color('TEXT', 'BLACK')
        self.colors.add_color('LINE', 'RED')

        self.bulletin_fetcher = BulletinFetcher(bdays_file, events_file, facts_file)
        self.min_bulletins = min_bulletins
        self.char_width = 8
        self.char_height = 8
        self.line_height = 10

        self.line_length = (self.width-(16*2)) // self.char_width
        self.message_formatter = setup_message_formatter(self.line_length, a_indent_str='', b_indent_str='')
        self.bulletins = None

    @property
    def _has_update(self):
        if ((not self.hardware.rtc.earth_time_mask.tm_hour) 
                or (not self.hardware.rtc.mars_time_mask.tm_hour)
                or (self.bulletins is None)):
            return 2
        return 0

    def _draw_full(self):
        if ((not self.hardware.rtc.earth_time_mask.tm_hour) 
                or (not self.hardware.rtc.mars_time_mask.tm_hour)
                or (self.bulletins is None)):
            # Clear existing subwidgets
            self._subwidgets = []
            # Load new bulletins
            self.bulletins = self.prepare_bulletins()
            if not self.bulletins:
                # If there are no bulletins, load the asterism widget
                self.add_subwidget(AsterismWidget(self.hardware, self.position, self.size, ))
        
        if self.bulletins:
            self.draw_bulletins(self.bulletins)

    def prepare_bulletins(self):
        # Load dated bulletins
        bulletins = self.bulletin_fetcher.collect_dated_bulletins(
            self.hardware.rtc.earth_time, self.hardware.rtc.mars_time)

        # If there are no dated bulletins, consider displaying constellations
        # Always consume a rand digit here to keep the clocks in sync
        show_constellations = MetaRand.rand_int(15) == 0
        if not bulletins and show_constellations:
            return []

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
        y_start = self.y
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
                self.display.text(line, ltext, pos, self.colors['TEXT'])
                if widget_loc:
                    self.apply_widget(x=((widget_loc-1)*self.char_width)+ltext,
                                      y=pos,
                                      w=embedded_widget)
                pos += self.line_height
            pos += wspace
            if b_num < len(bulletins) -1:
                self.display.line(200 - 30, pos, 200 + 30, pos, self.colors['LINE'])

    def apply_widget(self, x, y, w):
        widget, params = w.split(':', 1)

        if widget == 'MP':
            __, target_mon, target_mday = params.split('-')
            dt = next_date_occurrence(self.hardware.rtc.earth_time, int(target_mon), int(target_mday))
            widg = MoonPhaseWidget(self.hardware, (x, y), (self.char_width, self.char_height), outer=True, earth_time=dt )
            widg._draw_full()

        elif widget == 'SY':
            symbol = params
            widg = SymbolWidget(self.hardware, (x, y), (self.char_width, self.char_height),
                                 symbol, draw_bg=True)
            widg._draw_full()

        else:
            raise NotImplementedError(f"No widget for: {widget}")


class EmbeddedWidget:
    widget_pattern = re.compile(r'\+[\w:-]+\+')
    widget_placeholder_pattern = re.compile(r'\++')

    widget_placeholder_sizes = {
        'MP': 1,
        'SY': 1, 
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

