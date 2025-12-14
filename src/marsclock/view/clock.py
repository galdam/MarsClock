from marsclock.view.absview import AbsView
from marsclock.widget.datebar import DateBarWidget
from marsclock.widget.bulletin import BulletinWidget


class ClockView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)

        ## Solar Widget
        #solar_size = 80
        #solar_position = 200 - (solar_size // 2), 5

        self.add_subwidget(
            BulletinWidget(self.hardware, (0, 82), (self.width, 300-82)))

        self.add_subwidget(
            DateBarWidget(self.hardware, (0, 0), (self.width, 84)))
