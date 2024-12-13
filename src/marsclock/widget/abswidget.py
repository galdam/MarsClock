"""
AbsWidget: the base class for widgets.

WidgetColors:
"""


class WidgetColors:
    """

    """
    def __init__(self, palette):
        self._palette = palette
        self._colors = dict()

    def add_color(self, name, color):
        """

        Args:
            name:
            color:

        Returns:

        """
        color_value = self._palette.color(color)
        if color_value is None:
            raise ValueError(f"Palette has no color for '{name}': {color}")
        self._colors[name] = color_value

    def __getitem__(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self._colors[i]

# TODO A widget needs to be able to: Identify whether it is stale, Tell the display if it needs a full update


class AbsWidget:
    """

    """
    def __init__(self, hardware, position, size,):
        self.hardware = hardware
        self.display = self.hardware.display
        self.colors = WidgetColors(self.display.palette)
        self.position = position
        self.size = size
        self._widgets = []

    def add_widget(self, widget):
        self._widgets.append(widget)

    def draw(self):
        for widget in self._widgets:
            widget.draw()
        self._draw()

    def _draw(self):
        raise NotImplementedError()