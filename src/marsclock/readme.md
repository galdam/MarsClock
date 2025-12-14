
#### marsclock.astro: 

## Architecture

The following is an overview of the project structure.

#### upydrivers.display: DisplayDevice
The display device is an extension of the upy framebuffer. At its most abstract level, it should be feasible to replace it with any type of device. 

#### upydrivers.display: Palette
The base palette defines the 7 named colors available in the full color eink display and 2 levels of grey. There are implementations for each range of colors available for different types of eink screens. Where the number of colors on the screen is fewer than the full range, the colors are mapped to the most appropriate option.

#### marsclock.hardware: Hardware
The "Hardware" is the parent object that holds all of the interfaces with the physical components: the display, the RTC, and the buttons (if I get ground to adding them).

#### marsclock.view: View
A view is a special case of widget (see below). It collects together the elements that make up a page.

#### marsclock.widget: Widget
A widget is a visual component that can be drawn on the display. 
A widget can also have sub-widgets that are updated when the parent does.

#### marsclock.widget: WidgetColors
The widget colors holds colors with named roles that are required in the widget. 
Colors that are added to the widget colors must exist in the base palette.    
