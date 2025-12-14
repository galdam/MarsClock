from marsclock.astro.heliocentric import HeliocentricEarthMars
from marsclock.widget.abswidget import AbsWidget

# import framebuf


class HeliocentricEarthMarsWidget(AbsWidget):
    @property
    def minimum_size(self) -> tuple[int, int]:
        return 80, 80

    def __init__(self, hardware, position, size,
                 body_scale=0.03,
                 background_color='WHITE',
                 body_color='RED',
                 path_color='BLACK'):
        """
        """
        super().__init__(hardware, position, size)

        self.colors.add_color('BACKGROUND', background_color)
        self.colors.add_color('BODY', body_color)
        self.colors.add_color('PATH', path_color)
        self.diameter = min(self.height, self.width)
        self.radius = self.diameter // 2
        self.body_size = int(self.diameter*body_scale)
        
        # print(f'[HeliocentricEarthMarsWidget] body_size: {self.body_size}')

    def _draw_full(self):
        # self.display.apply_full_update()
        j2k = self.hardware.rtc.earth_time.j2kdelta
        hem = HeliocentricEarthMars(self.position, self.height, j2k)

        # Erase the background
        self.display.ellipse(*hem.sun(), self.radius, self.radius, self.colors['BACKGROUND'], True)

        # Draw the sun
        #self.display.ellipse(*hem.sun(), self.body_size, self.body_size, self.colors['BODY'], True)
        x, y = hem.sun()
        s = 'A'
        self.display.text_box(s, x-4, y-4, fg=self.colors['BACKGROUND'], bg=self.colors['BODY'], r=5, x_margin_padding=0, font_name='font_zodiac_8.bin')

        for planet in hem.PLANET_RADIUS_SCALE.keys():
            # Draw the path
            self.display.ellipse(*hem.planet_path(planet), self.colors['PATH'])

            # Erase the oldest part of the path
            for m in [0.02, 0.04, 0.06, 0.08, 0.1, ]:
                self.display.ellipse(*hem.planet_position(planet, m),
                                     self.body_size * 2, self.body_size * 2,
                                     self.colors['BACKGROUND'], True)

            x, y = hem.planet_position(planet)

            # Erase the area around the planet
            #self.display.ellipse(x, y, self.body_size*2, self.body_size*2, self.colors['BACKGROUND'], True)
            #self.display.ellipse(x, y, 12, 12, self.colors['BACKGROUND'], True)
            
            # Draw the planet
            #self.display.ellipse(x, y, self.body_size, self.body_size, self.colors['BODY'], True)
            s = {'Earth': 'D',  'Mars': 'E'}[planet]
            self.display.text_box(s, x-4, y-4, fg=self.colors['BACKGROUND'], bg=self.colors['BODY'], r=5, x_margin_padding=0, font_name='font_zodiac_8.bin')


