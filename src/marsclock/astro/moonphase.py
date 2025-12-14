"""
Estimate the phase of the moon.
"""

LEFT = 6
RIGHT = 9

class MoonPhase:
    """
    Approximate the phase of the moon on a given date.
    MoonPhase.moon_phase_pct ; convert a number of j2k days to the pct of moon phase
    """
    SYNODIC_MONTH = 29.53058861

    @classmethod
    def moon_phase_pct(cls, j2k_utc_days):
        """
        Convert the days since the epoch into
        the percentage of the way through the moon phase.
        0 is a new moon
        0.5 is a full moon
        """
        return ((j2k_utc_days + 22.9) % cls.SYNODIC_MONTH) / cls.SYNODIC_MONTH

    @classmethod
    def phase_to_str(cls, phase_pct):
        """

        """
        #synodic_month_pct = (phase_pct
        if phase_pct >= 0.95 or phase_pct < 0.05:
            return "New Moon"
        if phase_pct < 0.20:
            return "Waxing crescent"
        if phase_pct < 0.30:
            return "First quarter"
        if phase_pct < 0.45:
            return "Waxing gibbous"
        if phase_pct < 0.55:
            return "Full Moon"
        if phase_pct < 0.70:
            return "Waning gibbous"
        if phase_pct < 0.80:
            return "Last quarter"
        else:
            return "Waning crescent"

    @classmethod
    def calculate_moon_ellipse(cls, xo, yo, size, phase_pct, fg, bg, outer=True):
        """
        Get the series of ellipses to draw to represent a moon.
        Assumes that the background is white.
        Each phase can be represented as two half ellipses where one is full, and the other is squashed.

        xo, yo - int; x, y origin of where the moon should be drawn
        size - int; size of the moon to be drawn
        phase_pct - float; the percentage of the way through the moon phase
        """
        quart_pct = (phase_pct * 4) % 1
        r = size // 2
        x, y = xo+r, yo+r
        # Erase the background
        yield x, y, r, r, bg, True

        # Waxing crescent
        if phase_pct <= 0.25:
            yield x, y, r, r, fg, True, LEFT
            yield x, y, int(r * (1 - quart_pct)), r, fg, True, RIGHT
        # Waxing gibbous
        elif phase_pct <= 0.5:
            yield x, y, r, r, fg, True, LEFT
            yield x, y, int(r * quart_pct), r, bg, True, LEFT
        # Waning gibbous
        elif phase_pct <= 0.75:
            yield x, y, r, r, fg, True, RIGHT
            yield x, y, int(r * (1 - quart_pct)), r, bg, True, RIGHT
        # Waning crescent
        else:
            yield x, y, r, r, fg, True, RIGHT
            yield x, y, int(r * quart_pct), r, fg, True, LEFT
        # Draw the outer ring if enabled or if the moon  is new
        if outer or (phase_pct > 0.90 or phase_pct < 0.1):
            yield x, y, r, r, fg, False


"""
def run():
    epd = EPD()
    s = 20
    ss = 10
    for phase in range(10):
        x = int(s * phase + (s / 2)) * 2
        y = s
        draw_moon(epd, phase, x, y, ss)

    for phase in range(10):
        x = int(s * phase + (s / 2)) * 2
        y = s * 4
        draw_moon(epd, phase + 10, x, y, ss)

    for phase in range(9):
        x = int(s * phase + (s / 2)) * 2
        y = s * 8
        draw_moon(epd, phase + 20, x, y, ss)

    # for phase in range(15, 30):
    #    x = int(s*(phase-15)+(s/2))*2
    #    y = s*4
    #    draw_moon(epd, phase, x, y, s)

    epd.show()


def other_run():
    epd = EPD()
    epd.clear()

    x, y, s = 20, 20, 5
    day_root = 19829
    for i in range(15):
        day = day_root + i * 2

        phase = moon_phase_pct(day)
        draw_moon(epd, phase, x, y, s)
        epd.text(phase_to_str(phase), x + s + s, y - 5, CK)
        epd.text(' - '.join(map(str, time.gmtime(86400 * day)[0:3])), x + s + s, y + 5, CK)
        y += (s * 2)
    epd.show()
    # time.sleep_ms(5000)


def foo_draw_moon(epd, day):
    color = CK

    x, y = 200, 150
    xr, yr = 100, 100

    epd.ellipse(x, y, xr, yr, CK, True)
    epd.ellipse(x, y, xr, yr, CW, True, 3)
    epd.ellipse(x, y, xr, yr, CK, False)


if __name__ == "__main__":
    other_run()

"""