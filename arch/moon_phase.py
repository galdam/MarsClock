import time
from marsclock.hardware.driver.epaper import EPD, CK, CW

CK = 0
CW = 1

LEFT=6
RIGHT=9

synodic_month = 29.53059 
synodic_quart = (synodic_month * 0.25)




def calc_moon_phase(days_since_epoch):
    return (days_since_epoch +24) % synodic_month


def sydonic_pct(phase):
    return (phase % synodic_quart / synodic_quart)


def phase_to_str(phase):
    synodic_month_pct = (phase / synodic_month)
    if synodic_month_pct > 0.95 or synodic_month_pct < 0.05:
        return "New Moon"
    if synodic_month_pct < 0.20:
        return "Waxing crescent"
    if synodic_month_pct < 0.30:
        return "First quarter"
    if synodic_month_pct < 0.45:
        return "Waxing gibbous"
    if synodic_month_pct < 0.55:
        return "Full Moon"
    if synodic_month_pct < 0.70:
        return "Waning gibbous"
    if synodic_month_pct < 0.80:
        return "Last quarter"
    else :
        return "Waning crescent"


def draw_moon(epd, phase, xo, yo, size):
    r = int(size/2)
    x, y = xo+r, yo+r
    # Waxing cescent
    if phase <= (synodic_month * 0.25):
        #epd.ellipse(x, y, xr, yr, CK, True)
        epd.ellipse(x, y, r, r, CK, True, LEFT)
        epd.ellipse(x, y, int(r * (1 - sydonic_pct(phase))), r, CK, True, RIGHT)
    # Waxing gibbous
    elif phase <= (synodic_month * 0.5):
        #epd.ellipse(x, y, xr, yr, CK, True)
        epd.ellipse(x, y, r, r, CK, True, LEFT)
        epd.ellipse(x, y, int(r * (sydonic_pct(phase))), r, CW, True, LEFT)
    # Waning gibbous
    elif phase <= (synodic_month * 0.75):
        #epd.ellipse(x, y, xr, yr, CK, True)
        epd.ellipse(x, y, r, r, CK, True, RIGHT)
        epd.ellipse(x, y, int(r * (1 - sydonic_pct(phase))), r, CW, True, RIGHT)
    # Waning crescent
    else:
        epd.ellipse(x, y, r, r, CK, True, RIGHT)
        epd.ellipse(x, y, int(r * sydonic_pct(phase)), r, CK, True, LEFT)
    epd.ellipse(x, y, r, r, CK, False)


def run():
    epd = EPD()
    s = 20
    radius = 8
    for phase in range(10):
        x = int(s*phase+(s/2))*2
        y = s
        draw_moon(epd, phase, x, y, radius)
        
    for phase in range(10):
        x = int(s*phase+(s/2))*2
        y = s*4
        draw_moon(epd, phase+10, x, y, radius)
        
    
    for phase in range(9):
        x = int(s*phase+(s/2))*2
        y = s*8
        draw_moon(epd, phase+20, x, y, radius)
        
    
    #for phase in range(15, 30):
    #    x = int(s*(phase-15)+(s/2))*2
    #    y = s*4
    #    draw_moon(epd, phase, x, y, s)
    
    epd.show()
    
    
def other_run():
    epd = EPD()
    epd.clear()

    x, y, size = 5, 5, 8
    day_root = 19829
    for i in range(15):
        day = day_root+i*2
        phase = calc_moon_phase(day)
        draw_moon(epd, phase, x, y, size)
        epd.text(f"{phase_to_str(phase)} : {' - '.join(map(str, time.gmtime(86400 * day)[0:3]))}", x+size+2, y, CK)
        #epd.text(, x+s+s, y+5, CK)
        y += (size+2)
    epd.show()
    #time.sleep_ms(5000)
        
        
def foo_draw_moon(epd, day):
    color = CK
    
    x, y = 200, 150
    xr, yr = 100, 100
    
    epd.ellipse(x, y, xr, yr, CK, True)
    epd.ellipse(x, y, xr, yr, CW, True, 3)
    epd.ellipse(x, y, xr, yr, CK, False)

    

if __name__ == "__main__":
    other_run()