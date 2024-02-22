from display import Display
import time
from epaper import EPD, CK, CW


def test_loop(epd):    
    print('Write message one to buffer')
    epd.text("Waveshare", 5, 10, CK)
    epd.text("Pico_ePaper-4.2-B", 5, 40, CW)
    epd.text("Raspberry Pico", 5, 70, CK)
    print('Display message one')
    epd.show()
    time.sleep(5)


def run():
    print("Start ePaper")
    disp = Display()
    try:
        disp.loop()
    except Exception as err:
        print(f'Caught error:{err}')
        disp.shutdown()
        raise err
        
    finally:
        disp.shutdown()
    
if __name__ == '__main__':
    run()
