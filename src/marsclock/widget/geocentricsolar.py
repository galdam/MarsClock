# from marsclock.astro.heliocentric import HeliocentricEarthMars
import marsclock.helpers.math.mathplus as math
from marsclock.astro.ephemerisrelative import EphemerisRelative
from marsclock.widget.abswidget import AbsWidget
from marsclock.widget.zodiacdial import ZodiacDialWidget
from marsclock.widget.symbol import SymbolWidget

# import framebuf


class GeocentricSolarWidget(AbsWidget):
    @property
    def minimum_size(self) -> tuple[int, int]:
        return 80, 80

    CLASSICAL_PLANETS = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn']
    ALL_PLANETS = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

    def __init__(self, hardware, position, size,
                 fg=None, bg=None,
                 background_color='BLACK',
                 foreground_color='WHITE',
                 planet_color='RED',
                 observer='Earth', classical=True, reverse=True
                ):
        """
        """
        super().__init__(hardware, position, size)
        self.observer=observer
        self.classical = classical
        self.reverse = reverse


        self.r = min(self.size) // 2
        self.xo, self.yo = self.position[0]+self.r, self.position[1]+self.r
        self.zodiac_r = self.r-5

        self.colors.add_color('BG', background_color)
        self.colors.add_color('FG', foreground_color)
        self.colors.add_color('PLANET', planet_color)
        self.colors.add_color('PLANET_TEXT', 'WHITE')
        if self.colors['PLANET'] == self.colors['BG']:
            self.colors.add_color('PLANET', foreground_color)
            self.colors.add_color('PLANET_TEXT', background_color)
        elif self.colors['PLANET_TEXT'] == self.colors['PLANET']:
            self.colors.add_color('PLANET_TEXT', background_color)
    
        self.add_subwidget(
            ZodiacDialWidget(
                self.hardware, self.position, self.size, reverse=reverse, 
                foreground_color=foreground_color, background_color=background_color))
        self._assign_planetary_subwidgets()

        #self.colors.add_color('BACKGROUND', background_color)
        #self.colors.add_color('BODY', body_color)
        #self.colors.add_color('PATH', path_color)
        #self.body_size = int(self.height*body_size)
        # print(f'[HeliocentricEarthMarsWidget] body_size: {self.body_size}')

    @property
    def _has_update(self):
        if (not self.hardware.rtc.earth_time_mask.tm_mday):            
            return 2
        return 0

    
    def _draw_full(self):
        self.display.text("Geocentric", 250, 100, self.colors['FG'], v_spacing=-2, font_name='font_krungthep_14.bin')

    
    def _assign_planetary_subwidgets(self):
        planets = [p for p in (self.CLASSICAL_PLANETS if self.classical else self.ALL_PLANETS) if p != self.observer]
        j2k = self.hardware.rtc.earth_time.j2kdelta
        planet_angles = []
        for planet in planets:
            e = EphemerisRelative(self.observer, j2k, planet)
            planet_angles.append([e.distance_ecl, e.angle_ecl.rad, planet])
        planet_angles = sorted(planet_angles)

        m = -1 if self.reverse else 1
        planet_r_step = self.zodiac_r // (1+len(planet_angles))
        for i, p in enumerate(planet_angles):
            p_r = ((i+1) * planet_r_step)+4
            __, a, sy = p
            a = a + math.radians(-(90+30))
            
            self.add_subwidget(SymbolWidget(self.hardware, (
                 (self.xo-4)+int(m * (p_r * math.cos(a))), 
                 (self.yo-4)+int((p_r * math.sin(a)))), (8,9), 
                         sy, c=self.colors.get_color_name('PLANET_TEXT'), 
                         bg=self.colors.get_color_name('PLANET'), ))
        
        self.add_subwidget(SymbolWidget(self.hardware, (self.xo-4, self.yo-4), (8,9), 
                    'Earth', c=self.colors.get_color_name('PLANET_TEXT'), 
                    bg=self.colors.get_color_name('PLANET'), ))
