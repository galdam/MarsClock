from marsclock.view.absview import AbsView
from marsclock.widget.asterism import AsterismWidget
from marsclock.widget.datebar import DateBarWidget




class AsterismView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)


        self.add_subwidget(
            AsterismWidget(self.hardware, (0, 82), (self.width, 300-82)))

        self.add_subwidget(
            DateBarWidget(self.hardware, (0, 0), (self.width, 84)))