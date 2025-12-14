# from upydrivers.display.epaper.epd_UC8176_400x300_KW import DisplayDevice

from upydrivers.display.epaper.epd_SSD1683_400x300_KWC import DisplayDevice

from upydrivers.realtimeclock.rtc_ds3231 import RtcClockDevice
from marsclock.hardware.hardware import Hardware
from marsclock import runner


def run():
    print("Start MarsClock")
    #birthdays.add_birthdays()

    # Initialise the hardware object
    hardware = Hardware(
        display=DisplayDevice(rotation=0),
        rtc=RtcClockDevice()
    )

    try:
        runner.main_loop(hardware)
    except Exception as err:
        print(f'Caught error:{err}')
        hardware.display.shutdown()
        raise err
    finally:
        hardware.display.shutdown()

if __name__ == '__main__':
    run()
