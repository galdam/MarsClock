
Some resources to get started:
* https://en.wikipedia.org/wiki/Timekeeping_on_Mars
* https://en.wikipedia.org/wiki/Darian_calendar

This module works in two stages. Firstly, converting from 'Earth Time' to MTC (coordinated mars time). Secondly, converting from MTC to Darian Calendar.

## Coordinated Mars Time

In Martian time keeping; hours, minutes, and seconds are resized to match the length of the martian day (in Earth time: 24h 39m 35.244s). Sols (Martian days)are counted from 29 December 1873 (a date chosen from being prior to the 1877 perihelic opposition).
MTC is measured with the prime meridian at Airy-0 (AMT - Airy mean time).
The following is the NASA algorithm for making  this conversion: https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
* Get the current time as seconds since the unix epoch (1 Jan 1970)
* Convert to seconds since the Julian 2K epoch (12:00, 1 Jan 2000); the deltaJ2K. Julian dates do not use leap seconds or leap days so these may need to be correct for.
* Convert into MTC by shifting back to the martian epoch (29 Dec 1873) and converting by known scaling factors.
[(JDTT - 2451549.5) / 1.0274912517] + 44796.0 - 0.0009626 )

## Darian Calendar

Resources:
* Wikipedia:
  * https://en.wikipedia.org/wiki/Darian_calendar
* The white-paper for the Darian System:
  * https://www.researchgate.net/publication/290542846_The_Architecture_of_Time_Part_2_The_Darian_System_for_Mars
* A cute implementation:
  * https://marscalendar.sourceforge.io/
* Alternative example:
 http://interimm.org/mars-clock/en/cal-doc.html

Mars years in the Darian calendar use the 'telescopic' epoch, which uses Keplers observations of Mars as it's starting date. This has the advantage that it places Mars observations and events in positive values.
 1609; year 0 = Mars Year -183


# https://en.wikipedia.org/wiki/Timeline_of_space_exploration
