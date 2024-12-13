from marsclock.widget.abswidget import AbsWidget


class AbsView(AbsWidget):
    def __init__(self, hardware, position, size):
        super().__init__(hardware, position, size)

    @property
    def refresh_rate(self):
        """
        As some views might benefit from a faster refresh,
        it's a property of the view.
        """
        return 0.3

    def _draw(self):
        pass

