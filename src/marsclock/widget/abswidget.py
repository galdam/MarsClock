"""



WidgetColors:

AbsWidget: the base class for widgets.
"""
# TODO A widget needs to be able to: Identify whether it is stale, Tell the display if it needs a full update


class WidgetColors:
    """

    """
    def __init__(self, palette):
        self._palette = palette
        self._requested_colors = dict()
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
        self._requested_colors[name] = color
        self._colors[name] = color_value

    def get_color_name(self, name):
        return self._requested_colors[name]

    def __getitem__(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self._colors[i]



class AbsWidget:
    """

    """
    def __init__(self, hardware, position: (int, int), size: (int, int),):
        """

        Args:
            hardware:
            position: (int, int),  x and y
            size: (int, int),  width and height
        """
        self.hardware = hardware
        self.display = self.hardware.display
        self.position = position
        self.size = size
        self._validate_location()
        self.colors = WidgetColors(self.display.palette)
        self._subwidgets = []

    def _validate_location(self):
        """
        Check whether the widget location is valid for where it's been placed.
        """
        min_width, min_height = self.minimum_size
        disp_width, disp_height = self.display.width, self.display.height

        if ((self.width < min_width) or (self.height < min_height)
                or (self.x < 0) or (self.x + self.width > disp_width)
                or (self.y < 0) or (self.y + self.height > disp_height)):
            raise ValueError(''.join([
                "Invalid widget dimensions. ",
                f"Minimum size: ({min_width}, {min_height}). ",
                f"Requested size: ({self.width}, {self.height}). ",
                f"Display size: ({disp_width}, {disp_height}). ",
                f"Requested dimensions: (x: {self.x}, {self.x + self.width}; ",
                f"y: {self.y}, {self.y + self.height}).",
            ])
            )

    @property
    def minimum_size(self) -> (int, int):
        """
        The minimum valid size for this widget
        return: width,height
        """
        raise NotImplementedError("Minimum size must be defined.")

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    @property
    def x(self) -> int:
        return self.position[0]

    @property
    def y(self) -> int:
        return self.position[1]
    
    @property
    def has_update(self):
        return max(
            [self._has_update] 
            + [subwidget.has_update for subwidget in self._subwidgets])

    @property
    def _has_update(self):
        return 0
    
    def add_subwidget(self, subwidget):
        """
        Add a subwidget that will be updated when this widget is updated.
        Args:
            subwidget:
        Returns:
        """
        self._subwidgets.append(subwidget)

    def draw(self, update_type):
        """
        Activate the _draw function for this widget and all sub-widgets
        Returns:
        """
        if update_type == 1:
            self._draw_partial()
        elif update_type == 2:
            self._draw_full()
        else:
            raise ValueError()
        for subwidget in self._subwidgets:
            subwidget.draw(update_type)

    def _draw_partial(self):
        """Draw this widget"""
        pass

    def _draw_full(self):
        """Draw this widget"""
        pass