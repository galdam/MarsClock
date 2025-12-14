from marsclock.view.absview import AbsView
from marsclock.widget.datebar import DateBarWidget
from marsclock.widget.geocentricsolar import GeocentricSolarWidget
from marsclock.widget.symbol import SymbolKeyWidget

class GeocentricView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)

        self.add_subwidget(
            DateBarWidget(self.hardware, (0, 0), (self.width, 80)))
        
        r = 210//2
        self.add_subwidget(
            GeocentricSolarWidget(self.hardware, (15, 85), (r*2, r*2), 
                                background_color='WHITE', 
                                foreground_color='BLACK'))

        self.add_subwidget(
            SymbolKeyWidget(self.hardware, (400-150-15, 300-135), (150, 124)))
        
    def _draw(self):
        self.hardware.display.text(
            "Geocentric", 250, 100, self.display.palette.BLACK, 
            spacing=-2, font_name='font_krungthep_14.bin')
