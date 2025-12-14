from marsclock.astro.moonphase import MoonPhase
from marsclock.widget.abswidget import AbsWidget


class MoonPhaseWidget(AbsWidget):

    @property
    def minimum_size(self) -> (int, int):
        """
        Returns: (int, int), width, height,
        """
        return 8,8

    def __init__(self, hardware, position, size, outer=False, earth_time=None):
        super().__init__(hardware, position, size)
        self.colors.add_color('FG', 'BLACK')
        self.colors.add_color('BG', 'WHITE')
        self.diameter = min(size)
        #self.radius = min(size) // 2
        self.outer = outer
        #self.origin = self.position[0] + self.radius, self.position[1] + self.radius
        self.earth_time=earth_time

    @property
    def _has_update(self):
        if (not self.hardware.rtc.earth_time_mask.tm_mday):            
            return 2
        return 0

    def _draw_full(self):
        if self.earth_time is None:
            epoch_days = self.hardware.rtc.earth_time.epoch_tc_days
        else:
            epoch_days = self.earth_time.epoch_tc_days
            
        mp = MoonPhase()
        phase_pct = mp.moon_phase_pct(epoch_days)
        for params in mp.calculate_moon_ellipse(
                    *self.position, self.diameter, phase_pct,
                    self.colors['FG'], self.colors['BG'], self.outer):
            self.display.ellipse(*params)
