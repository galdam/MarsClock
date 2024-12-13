"""
NOTE: This is only compatible with the v2 version of this display.
For v1, see Controller UC8176.

This driver is compatible with ePaper screens
using controller SSD1683:
    - WaveShare 4.2inch Black/White,4 Grayscale 400x300 v2
        - https://www.waveshare.com/wiki/Pico-ePaper-4.2
        - https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_Manual
    - GooDisplay 4.2in Black/White,4 Grayscale 400x300 GDEQ042T81
        - https://www.good-display.com/product/443.html

Controller SSD1683:


Other examples of code that supports this display:
https://github.com/waveshareteam/Pico_ePaper_Code/blob/main/python/Pico-ePaper-4.2_V2.py
https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd4in2_V2.py
https://github.com/peterhinch/micropython-micro-gui/blob/main/drivers/epaper/pico_epaper_42_v2.py
https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42_v2.py
https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42_v2_gs.py
"""