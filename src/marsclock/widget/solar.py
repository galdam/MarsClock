from marsclock.astro.solar import Solar


class SolarWidget(Solar):
    def __init__(self, hardware, position, size,
                 background_color='WHITE',
                 body_color='RED',
                 path_color='BLACK'):
        """

        Args:
            hardware:
            position: The
            size:
        """

        self.hardware = hardware
        self.display = self.hardware.display

        palette = self.display.palette
        self.background_color = palette.color(background_color)
        self.body_color = palette.color(body_color)
        self.path_color = palette.color(path_color)


        # Solar
        super().__init__(position, size,)

    def draw(self):
        # time.localtime(time.mktime(self.earth_time))
        earth_days = self.hardware.rtc.earth_time.tm_yday
        mars_days = self.hardware.rtc.mars_time.tm_yday

        ps = 4
        # Draw the sun in
        self.display.ellipse(*self.sun(), ps, ps, self.background_color, True)
        for planet, days in [('mars', mars_days), ('earth', earth_days)]:
            # Draw the path
            self.epd.ellipse(*self.planet_path(planet), self.path_color)
            # Erase the area around the planet, shifted to erase more of the oldest part of the path
            self.epd.ellipse(*self.planet_loc(planet, days+20), ps * 2, ps * 2, self.background_color, True)
            # Draw the planet
            self.epd.ellipse(*self.planet_loc(planet, days), ps, ps, self.body_color, True)
