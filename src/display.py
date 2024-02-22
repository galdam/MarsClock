import marstime
import time
from solarwidget import SolarWidget
from epaper import EPD, CK, CW
from machine import Pin, I2C
from ds3231_gen import DS3231
import font_krungthep14
import framebuf
from font_writer import Writer
import messages
import constellationwidget
import random


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
    def __init__(self):
        # Load Hardware
        self.epd = EPD()
        self.buttons = ButtonListener()
        self.ds3231 = DS3231()
        # print(self.ds3231.get_time())

        self.demo_mode = False
        self.margin = 16

        # Solar Widget
        self.solar_size = 70
        self.solar_position = 200 - (self.solar_size // 2), 10
        self.solar_widget = SolarWidget(self.solar_size, self.solar_position)

        self.earth_time, self.mars_time = self._get_times()

        self.krungthep_writer = Writer(self.epd, font_krungthep14)

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

    def _draw_solar_system(self):
        earth_days = self.earth_time.tm_yday
        mars_days = self.mars_time.tm_yday

        ps = 4
        # Draw the sun in
        self.epd.ellipse(*self.solar_widget.sun(), ps, ps, CK, True)
        for planet, days in [('mars', mars_days), ('earth', earth_days)]:
            # Draw the path
            self.epd.ellipse(*self.solar_widget.planet_path(planet), CK)
            # Erase the area around the planet
            self.epd.ellipse(*self.solar_widget.planet_loc(planet, days), ps + 3, ps + 3, CW, True)
            # Draw the planet
            self.epd.ellipse(*self.solar_widget.planet_loc(planet, days), ps, ps, CK, True)

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
        self.write_centered_str(c_x, y, earth_clock)
        self.write_centered_str(400 - c_x, y, mars_clock)

    def write_centered_str(self, center_x, y, text):
        x = int(center_x - (( 13 * len(text) ) / 2))
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

        earth_dt = marstime.EarthCal.print_datetime(self.earth_time)
        mars_dt = marstime.MarsCal.print_datetime(self.mars_time)

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
        self._draw_solar_system()
        self.draw_date_info()

        msgs = messages.select_messages(self.earth_time, self.mars_time)
        if msgs is None:
            starmaps=[
            'bootes','cepheus', 'draco',
            'gemini', 'orion', 'ursaminor'
            ]
            constellation=random.choice(starmaps)
            constellationwidget.draw_star_chart(self.epd, (15, 85), constellation)
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


def test_loop(epd):
    print('Write message one to buffer')
    epd.text("Waveshare", 5, 10, CK)
    epd.text("Pico_ePaper-4.2-B", 5, 40, CW)
    epd.text("Raspberry Pico", 5, 70, CK)
    print('Display message one')
    epd.show()
    time.sleep(5)


"""if key_state['key0'][0] & key_state['key0'][1]:
                print('Key0 Pressed')
            if key_state['key1'][0] & key_state['key1'][1]:
                print('Key1 Pressed')
            if key_state['key0'][0] & key_state['key1'][0]:
                print('Both Keys 0 and 1 Pressed')
                break
"""


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
