from marsclock.astro.heliocentric import HeliocentricEarthMars
from marsclock.widget.abswidget import AbsWidget

# import framebuf


class HeliocentricEarthMarsWidget(AbsWidget):
    def __init__(self, hardware, position, size,
                 body_size=0.02,
                 background_color='WHITE',
                 body_color='RED',
                 path_color='BLACK'):
        """
        """
        super().__init__(hardware, position, size)

        self.colors.add_color('BACKGROUND', background_color)
        self.colors.add_color('BODY', body_color)
        self.colors.add_color('PATH', path_color)

        self.body_size = int(size*body_size)

    def _draw(self):
        self.display.apply_full_update()
        j2k = self.hardware.rtc.earth_time.j2kdelta
        hem = HeliocentricEarthMars(self.position, self.size, j2k)

        # Erase the background
        self.display.ellipse(
            *hem.sun(), self.size // 2, self.size // 2,
            self.colors['BACKGROUND'], True)

        # Draw the sun in
        self.display.ellipse(
            *hem.sun(), self.body_size, self.body_size,
            self.colors['BACKGROUND'], True)

        for planet in hem.PLANET_RADIUS_SCALE.keys():
            # Draw the path
            self.display.ellipse(
                *hem.planet_path(planet), self.colors['PATH'])

            # Erase the oldest part of the path
            for m in [0.02, 0.04]:
                self.display.ellipse(
                    *hem.planet_position(planet, m),
                    self.body_size * 2, self.body_size * 2,
                    self.colors['BACKGROUND'], True)

            x, y = hem.planet_position(planet)

            # Erase the area around the planet
            self.display.ellipse(
                x, y, self.body_size*2, self.body_size*2,
                self.colors['BACKGROUND'], True)

            # Draw the planet
            self.display.ellipse(
                x, y, self.body_size, self.body_size,
                self.colors['BODY'], True)
