"""
AbsView: Abstract class for view objects. 
This is a special case of widget that serves as a top level object that represents a page.
"""

from marsclock.widget.abswidget import AbsWidget


class AbsView(AbsWidget):
    """
    A view is a top level widget
    """
    def __init__(self, hardware):
        position = 0,0
        size = hardware.display.width, hardware.display.height, 
        # position: (int, int),  x and y
        # size: (int, int),  width and height
        super().__init__(hardware, position, size)

    @property
    def refresh_rate(self):
        """
        As some views might benefit from a faster refresh,
        it's a property of the view.
        """
        return 0.3

    @property
    def minimum_size(self):
        """
        The minimum valid size for this widget
        return: width,height
        """
        return 0,0
    
    def action(self):
        pass
