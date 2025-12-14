from marsclock.view.absview import AbsView
from marsclock.widget.datebar import DateBarWidget
from marsclock.widget.heliocentricsolar import HeliocentricSolarWidget
from marsclock.widget.symbol import SymbolKeyWidget

class HeliocentricView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)

        self.add_subwidget(
            DateBarWidget(self.hardware, (0, 0), (self.width, 80)))
        
        r = 210//2
        self.add_subwidget(
            HeliocentricSolarWidget(self.hardware, (int(400-((r*2)+15)), 85), (r*2, r*2), 
                                background_color='WHITE', 
                                foreground_color='BLACK'))

        self.add_subwidget(
            SymbolKeyWidget(self.hardware, (15, 300-135), (150, 124)))
        
    def _draw(self):
        self.hardware.display.text(
            "Heliocentric", 30, 100, self.display.palette.BLACK, 
            spacing=-2, font_name='font_krungthep_14.bin')
