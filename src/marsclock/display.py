import time

from marsclock import marstime

from marsclock.drivers.pico_epaper_42_BRW import EPD
from marsclock.drivers.ds3231_gen import DS3231, MockDS3231
from marsclock.drivers.button import ButtonListener

from marsclock.fonts.font_writer import Writer
from marsclock.fonts import font_krungthep14

from marsclock.widgets.solarwidget import SolarWidget
from marsclock.widgets.constellationwidget import ConstellationWidget
from marsclock.content import messages


CW = 0
CB = 1
CR = 1

class Display:
    def __init__(self):
        # Load Hardware
        self.epd = EPD()
        self.buttons = ButtonListener()
        try:
            self.ds3231 = DS3231()
        except RuntimeError as err:
            print(err)
            self.ds3231 = MockDS3231()

        self.demo_mode = False
        self.margin = 16

        self.earth_time, self.mars_time = self._get_times()

        # Solar Widget
        self.solar_size = 70
        self.solar_position = 200 - (self.solar_size // 2), 10
        self.solar_widget = SolarWidget(self.epd, self.solar_size, self.solar_position)

        # Constellation Widget
        self.constellation_widget = ConstellationWidget(self.epd, (15, 85))

        self.fonts = {'krungthep14': Writer(self.epd, font_krungthep14)}
        self.title_font = 'krungthep14'


    def _time_diff_mask(self):
        et, mt = self._get_times()
        mask = [marstime.compare_datetimes(self.earth_time, et),
                marstime.compare_datetimes(self.mars_time, mt)]
        self.earth_time, self.mars_time = et, mt
        return mask

    def _get_times(self):
        et = marstime.DateTimeTup(*self.ds3231.get_time())
        mt = marstime.MarsCal.from_earthtime(et)
        return et, mt


    def draw_time(self):
        ltext = self.margin
        rtext = 400 - (ltext + (16 * 8))
        if self.demo_mode:
            fmt = '{tm_hour:0>2d}:{tm_min:0>2d}:{tm_sec:0>2d}'
        else:
            fmt = '{tm_hour:0>2d}:{tm_min:0>2d}'#:{tm_sec:0>2d}'
        earth_clock = fmt.format(tm_hour=self.earth_time.tm_hour,
                                 tm_min=self.earth_time.tm_min,
                                 tm_sec=self.earth_time.tm_sec)

        mars_clock = fmt.format(tm_hour=self.mars_time.tm_hour,
                                 tm_min=self.mars_time.tm_min,
                                 tm_sec=self.mars_time.tm_sec)

        y = 42
        c_x = ltext + (((200 - 30)-ltext)/2)
        self.write_centered_str(self.title_font, c_x, y, earth_clock)
        self.write_centered_str(self.title_font, 400 - c_x, y, mars_clock)

    def write_centered_str(self, font, center_x, y, text):
        char_width = self.fonts[font].font.max_width()
        x = int(center_x - (( char_width * len(text) ) / 2))
        self.fonts[font].print(text,x, y)

    def draw_mirrored_hline(self, x_start, x_end, y):
        self.epd.line(x1=x_start, y1=y, x2=x_end, y2=y, c=CB)
        self.epd.line(x1=400-x_end, y1=y, x2=400-x_start, y2=y, c=CB)


    def draw_date_info(self):
        ltext = self.margin
        rtext = 400 - (ltext + (16 * 8))

        y = 10
        self.draw_mirrored_hline(ltext, 200 - 30, y)

        earth_dt = marstime.EarthCal.print_datetime(self.earth_time)
        mars_dt = marstime.MarsCal.print_datetime(self.mars_time)

        y = 20
        self.epd.text(s='{:>16}'.format(earth_dt[0]), x=ltext, y=y, c=CB)
        self.epd.text(s='{:<16}'.format(mars_dt[0]), x=rtext, y=y, c=CB)

        y = 30
        self.epd.text(s='{:>16}'.format(earth_dt[1]), x=ltext, y=y, c=CB)
        self.epd.text(s='{:<16}'.format(mars_dt[1]), x=rtext, y=y, c=CB)

        self.draw_time()

        y = 60
        c_x = ltext + (((200 - 30)-ltext)/2)
        self.write_centered_str(self.title_font, c_x, y, earth_dt[3])
        self.write_centered_str(self.title_font, 400 - c_x, y, mars_dt[3])

        y = 80
        self.draw_mirrored_hline(ltext, 200 - 30, y)


    def draw_messages(self, paragraph):
        ltext = self.margin

        line_start = 82
        lines = sum(len(p) for p in paragraph) + (2*(len(paragraph) - 1))
        line_num = (22 - lines) // 2

        for i, p in enumerate(paragraph):
            for line in p:
                self.epd.text(s=line, x=ltext, y=line_start + (line_num * 9), c=CB)
                line_num += 1
            if 1+i < len(paragraph):
                line_num += 1
                y = line_start + (line_num * 9)
                self.epd.line(x1=200-30, y1=y, x2=200+30, y2=y, c=CB)
                line_num += 1

        y = 300 - 10
        self.epd.line(x1=self.margin, y1=y, x2=400 - self.margin, y2=y, c=CB)

    def update_time(self):
        self.epd.set_partial_update()
        self.draw_time()
        self.epd.show()

    def refresh_time(self):
        self.epd.set_full_update()
        self.draw_time()
        self.epd.show()

    def update_all(self):
        self.epd.set_full_update()
        self.epd.fill(CW)
        self.solar_widget.draw(self.earth_time, self.mars_time)
        self.draw_date_info()

        msgs = messages.select_messages(self.earth_time, self.mars_time)
        if msgs is None:
            self.constellation_widget.draw(self.constellation_widget.pick_constellation())
        else:
            paragraphs = [messages.format_message(m) for m in msgs]
            self.draw_messages(paragraphs)
        self.epd.show()

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
                if not mm[3]:
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
