from marsclock.astro.moonphase import MoonPhase
from marsclock.widget.abswidget import AbsWidget


class MoonPhaseWidget(AbsWidget):
    def __init__(self, hardware, position, size, outer=False):
        super().__init__(hardware, position, size)
        self.colors.add_color('FG', 'BLACK')
        self.colors.add_color('BG', 'WHITE')
        self.outer = outer

    def _draw_widget(self):
        mp = MoonPhase()
        epoch_days = self.hardware.rtc.earth_time.epoch_tc_days
        phase_pct = mp.moon_phase_pct(epoch_days)
        for params in mp.calculate_moon_ellipse(
                    *self.position, self.size, phase_pct,
                    self.colors['FG'], self.colors['BG'], self.outer):
            self.display.ellipse(*params)
