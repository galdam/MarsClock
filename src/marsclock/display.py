#from marsclock import marstime
import time
from machine import Pin

from marsclock.astro import astrotime
from marsclock.astro.strfmtastrotime import StrFmtTime
from marsclock.widget.solar import SolarWidget
from marsclock.widget.bulletin import BulletinWidget
from marsclock.widget.moonphase import MoonPhaseWidget
from marsclock.hardware.driver.epaper import EPD, CK, CW
from marsclock.hardware.driver.ds3231_gen import DS3231
from marsclock.hardware.driver import font_krungthep14
from marsclock.hardware.driver.font_writer import Writer
from marsclock.mathutils import MetaRand



class ButtonListener:
    def __init__(self):
        self.pins = {
            'key0': Pin(15, Pin.IN, Pin.PULL_UP),  # GP15
            'key1': Pin(17, Pin.IN, Pin.PULL_UP),  # GP17
        }
        self.states = {k: 1 for k in self.pins.keys()}

    def __get_pin_state(self, k):
        state = self.pins[k].value() == 0
        updated = state == self.states[k]
        self.states[k] = state
        return state, updated

    def get_states(self):
        return {k: self.__get_pin_state(k) for k in self.pins}


class Display:
    """
    The main class that brings all the elements together.
    """
    def __init__(self):
        # Load Hardware
        self.epd = EPD()
        self.buttons = ButtonListener()
        self.ds3231 = DS3231()
        self.is_bst = None
        self.earth_time, self.mars_time = self._get_times()
    
        # print(self.ds3231.get_time())

        self.demo_mode = False
        self.partial_refresh_count = 0
        self.margin = 16

        self.krungthep_writer = Writer(self.epd, font_krungthep14)
        self.widgets = []

        # Solar Widget
        solar_size = 80
        solar_position = 200 - (solar_size // 2), 5

        self.widgets.append(SolarWidget(self, solar_size, solar_position),)
        self.widgets.append(BulletinWidget(self, 0, 0))
        self.widgets.append(MoonPhaseWidget(self, 16, (20, 20)))

        self.time_formatters = [
            StrFmtTime("%A"),  # f'{day_name}',
            StrFmtTime("%d %B"),  # f'{dt.tm_mday} {month_name}',
            StrFmtTime("%H:%M"),  # f'{dt.tm_hour:0>2d}:{dt.tm_min:0>2d}',#:{dt.tm_sec:0>2d}',
            StrFmtTime("%Y/%m/%d"),  # f'{dt.tm_year}/{dt.tm_mon:0>2d}/{dt.tm_mday:0>2d}',
        ]

    @staticmethod
    def compare_datetimes(time_a, time_b):
        return [a == b for a, b in zip(time_a.to_tuple(), time_b.to_tuple())]

    def _time_diff_mask(self):
        et, mt = self._get_times()
        mask = [self.compare_datetimes(self.earth_time, et),
                self.compare_datetimes(self.mars_time, mt)]
        self.earth_time, self.mars_time = et, mt
        return mask

    def _get_times(self):
        """
        """
        earth_dt = astrotime.EarthDateTime(*self.ds3231.get_time_tup()[:6],
                                           tm_offset=3600 if self.is_bst else 0)
        if self.is_bst is None:
            self.is_bst = astrotime.is_bst(earth_dt)
            print(f"Is BST: {self.is_bst}")
            if self.is_bst:
                earth_dt = astrotime.EarthDateTime(*self.ds3231.get_time_tup()[:6],
                                                   tm_offset=3600 if self.is_bst else 0)
        mars_dt = earth_dt.to_marstime()
        return earth_dt, mars_dt


    def draw_time(self):
        ltext = self.margin
        if self.demo_mode:
            fmt = '{tm_hour:0>2d}:{tm_min:0>2d}:{tm_sec:0>2d}'
        else:
            fmt = '{tm_hour:0>2d}:{tm_min:0>2d}'
        earth_clock = fmt.format(tm_hour=self.earth_time.tm_hour,
                                 tm_min=self.earth_time.tm_min,
                                 tm_sec=self.earth_time.tm_sec)

        mars_clock = fmt.format(tm_hour=self.mars_time.tm_hour,
                                 tm_min=self.mars_time.tm_min,
                                 tm_sec=self.mars_time.tm_sec)

        y = 42
        c_x = ltext + (((200 - 30)-ltext)/2)
        self.write_centered_str(c_x, y, earth_clock)
        self.write_centered_str(400 - c_x, y, mars_clock)

    def write_centered_str(self, center_x, y, text):
        x = int(center_x - (( 13 * len(text)) / 2))
        self.krungthep_writer.set_textpos(self.epd, y, x)
        self.krungthep_writer.printstring(text, invert=True)

    def draw_mirrored_hline(self, x_start, x_end, y):
        self.epd.line(x_start, y, x_end, y, CK)
        self.epd.line(400-x_end, y, 400-x_start, y, CK)


    def draw_date_info(self):
        ltext = self.margin
        rtext = 400 - (ltext + (16 * 8))

        y = 10
        self.draw_mirrored_hline(ltext, 200 - 30, y)

        #earth_dt = marstime.EarthCal.print_datetime(self.earth_time)
        #mars_dt = marstime.MarsCal.print_datetime(self.mars_time)

        earth_dt = [fmt.format_time(self.earth_time)
                    for fmt in self.time_formatters]
        mars_dt = [fmt.format_time(self.mars_time)
                   for fmt in self.time_formatters]

        y = 20
        self.epd.text('{:>16}'.format(earth_dt[0]), ltext, y, CK)
        self.epd.text('{:<16}'.format(mars_dt[0]), rtext, y, CK)

        y = 30
        self.epd.text('{:>16}'.format(earth_dt[1]), ltext, y, CK)
        self.epd.text('{:<16}'.format(mars_dt[1]), rtext, y, CK)

        self.draw_time()

        y = 60
        c_x = ltext + (((200 - 30)-ltext)/2)
        self.write_centered_str(c_x, y, earth_dt[3])
        self.write_centered_str(400 - c_x, y, mars_dt[3])

        y = 80
        self.draw_mirrored_hline(ltext, 200 - 30, y)

    """
    def draw_messages(self, paragraph):
        ltext = self.margin
        line_start = 82
        lines = sum(len(p) for p in paragraph) + (2*(len(paragraph) - 1))
        line_num = (22 - lines) // 2

        for i, p in enumerate(paragraph):
            for line in p:
                self.epd.text(line, ltext, line_start + (line_num * 9), CK)
                line_num += 1
            if 1+i < len(paragraph):
                line_num+=1
                y = line_start + (line_num * 9)
                self.epd.line(200-30, y, 200+30, y, CK)
                line_num += 1

        y = 300 - 10
        self.epd.line(self.margin, y, 400 - self.margin, y, CK)
    """

    def update_screen(self, full=False):
        if not full and self.partial_refresh_count < 30:
            self.epd.set_partial_update()
            self.partial_refresh_count += 1
        else:
            self.epd.set_full_update()
            self.partial_refresh_count = 0
        self.epd.show()

    def update_time(self):
        self.draw_time()
        self.update_screen(full=False)

    def refresh_time(self):
        self.draw_time()
        self.update_screen(full=True)

    def update_all(self):
        self.epd.fill(CW)
        self.is_bst = astrotime.is_bst(self.earth_time)
        MetaRand.set_seed(self.earth_time.epoch_tc_hours)
        for widget in self.widgets:
            widget.draw()
        self.draw_date_info()
        """
        msgs = messages.select_messages(self.earth_time, self.mars_time)
        if msgs is None:
            starmaps=[
            'bootes','cepheus', 'draco',
            'gemini', 'orion', 'ursaminor'
            ]
            constellation=random.choice(starmaps)
            constellation.draw_star_chart(self.epd, (15, 85), constellation)
        else:
            paragraphs = [messages.format_message(m) for m in msgs]
            self.draw_messages(paragraphs)
        """
        self.update_screen(full=True)

    def shutdown(self):
        self.epd.set_full_update()
        print("Clear screen")
        #self.epd.fill(CK)
        #self.epd.show()
        #time.sleep(2)
        self.epd.clear()
        print("Shutting down")
        self.epd.sleep()
        print("~ DONE ~")

    def loop(self):
        self.update_all()

        while True:
            key_state = self.buttons.get_states()
            if key_state['key0'][0] and key_state['key1'][0]:
                print('Both pressed, shutting down')
                break

            if key_state['key0'][0]:
                self.demo_mode = True

            em, mm = self._time_diff_mask()
            # 0:year, 1:mon, 2:mday, 3:hour, 4:min, 5:sec
            # If there's an update to 0:year, 1:mon, 2:mday,
            if not all(em[:3]) or not all(mm[:3]):
                self.update_all()
            # If demo mode is enabled:
            elif self.demo_mode:
                # Update messages every martian minute
                if not mm[4]:
                    self.update_all()
                # Full refresh the screen if the hour or minute changes 
                elif not all([em[3], em[4], mm[3], mm[4]]):
                    self.refresh_time()
                # Partial update of the time if the second changes
                elif not em[5] or not mm[5]:
                    self.update_time()
            else:
                # Update the messages if the mars hour changes
                if not em[3]:
                    self.update_all()
                # Full refresh of the screen on the hour
                elif not em[3] or not mm[3]:
                    self.refresh_time()
                # Partial update of screen on the minute
                elif not em[4] or not mm[4]:
                    self.update_time()

            time.sleep_ms(10)



def run():
    print("Start ePaper")
    disp = Display()
    try:
        disp.loop()
    except Exception as err:
        print(f'Caught error:{err}')
        disp.shutdown()
        raise err

    finally:
        disp.shutdown()

if __name__ == '__main__':
    run()

