
from marsclock.view.absview import AbsView
from marsclock.widget.abswidget import AbsWidget
from marsclock.widget.datebar import DateBarWidget

class WelcomeView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.add_subwidget(
            DateBarWidget(self.hardware, (0, 0), (self.width, 84)))
        
        self.add_subwidget(
            WecomeWidget(self.hardware, (0, 0), (self.width, self.height)))


class WecomeWidget(AbsWidget):
    @property
    def minimum_size(self) -> tuple[int, int]:
        return 400, 300
    
    def __init__(self, hardware, position, size):
        super().__init__(hardware, position, size)
        self.colors.add_color('FG', 'BLACK')
        self.colors.add_color('BG', 'WHITE')

    def _draw_full(self):
        fg = self.colors['FG']
        disp = self.display
        disp.line(25, 30, 25, 154, fg)
        disp.line(25, 154, 30, 154, fg)
        disp.text('Phase of the moon (Earth)', 35, 150, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)
        
        disp.line(50, 90, 50, 120, fg)
        disp.line(40, 90, 140, 90, fg)
        disp.line(40, 90, 40, 87, fg)
        disp.line(140, 90, 140, 87, fg)
        disp.text('Sun rise/ set (Earth)\nLocation is configurable', 40, 124, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)

        disp.line(155, 30, 155, 100, fg)
        disp.line(155, 30, 150, 30, fg)
        disp.line(150, 15, 147, 15, fg)
        disp.line(150, 60, 147, 60, fg)
        disp.line(150, 15, 150, 60, fg)
        disp.text('Earth date and time', 60, 104, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)

        disp.line(400-155, 30, 400-155, 100, fg)
        disp.line(400-155, 30, 400-150, 30, fg)
        disp.line(400-150, 15, 400-147, 15, fg)
        disp.line(400-150, 60, 400-147, 60, fg)
        disp.line(400-150, 15, 400-150, 60, fg)
        disp.text('Martian date and time\nby the Darian Calendar', 220, 104, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)

        disp.line(355, 90, 355, 130, fg)
        disp.line(260, 90, 360, 90, fg)
        disp.line(260, 90, 260, 87, fg)
        disp.line(360, 90, 360, 87, fg)
        disp.text('Mars rise/set (Earth)', 250, 134, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)

        disp.line(200, 85, 200, 154, fg)
        disp.line(200, 154, 205, 154, fg)
        disp.text('Relative positions\nof Earth and Mars',210, 150, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)
        
        welcome_start = 200 #180
        disp.text('Welcome', 30, welcome_start, fg, font_name='font_krungthep_14.bin', h_spacing=-1)
        disp.text('to the Mars clock', 30+90, welcome_start+5, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)

        disp.text("If you've ever wondered what time it is on Mars...", 
                    30, welcome_start+30, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)
        disp.text("now you know.", 
                    290, welcome_start+40, fg, 
                    font_name='font_adafruit_5x8.bin', h_spacing=1)
