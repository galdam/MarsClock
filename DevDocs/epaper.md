
Glossary:

- VCOM: the voltage input. It is the common electrode on the front side of the display, and it provides the reference voltage against which the driving voltages act. 
- Source and Gate: Gate drivers are arranged along the vertical axis, one on each row. Gates are triggered one at a time. The source drivers are arranged along the horizontal axis, one for each column of pixels. Source drivers are activated at the same time.
- LUT : Look up table.
- Booster : the supply of charge. Should be powered off between screen refreshes.


See this article for a high level introduction to the gate/source:
- http://essentialscrap.com/eink/electronics.html

For how these voltage differentials result in eink pixels changing color, see:
- https://benkrasnow.blogspot.com/2017/10/fast-partial-refresh-on-42-e-paper.html

In short, for each pixel, the lookup table is consulted for the pattern of voltages that will result in the correct particles rising to the top: the positively charged black or the negatively charged white. There are also big positively charged red particles that can be shown by pulling the black and red up and then pull the black bits down again. Because they're smaller, they're easier to move and the red stay at the top. This is also why black/white partial refreshes are possible but not red.

For more on LUTs, see:
-https://github.com/olikraus/u8g2/issues/1393

Most of the GooDisplay and WaveShare screens use an UltraChip all-in-one IC with timing control. The drivers are fairly similar at an overview with many of the same elements and commands.

Booster & Regulator: Stores charge
Source Driver : sends signal down the columns
Gate driver : sends signal along the rows
OTP: One time program, preset memory
LUT: Lookup table of patterns
VCOM: Voltage across the front of the screen.
Frame  Memory: the SRAM where the graphics are stored.

LUT data is picked for the pixel color that is being changed too and from, and for the current temperature.

- https://github.com/antirez/uc8151_micropython




- https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42.py
- https://github.com/peterhinch/micropython-epaper
- https://github.com/waveshare/Pico_ePaper_Code.git


- https://github.com/mcauser/micropython-waveshare-epaper/blob/master/epaper4in2.py

- https://benkrasnow.blogspot.com/2017/10/fast-partial-refresh-on-42-e-paper.html
- https://github.com/pskowronek/epaper-clock-and-more/blob/master/epds/epd2in7b_fast_lut.py
- https://github.com/rdagger/MicroPython-2.9-inch-ePaper-Library

- https://github.com/CursedHardware/epd-datasheet/blob/main/epd-display.csv


- https://github.com/zhufucdev/gdey075z08_driver/tree/main

https://github.com/olikraus/u8g2/issues/1393