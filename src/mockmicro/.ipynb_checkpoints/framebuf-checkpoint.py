# SPDX-FileCopyrightText: <text> 2018 Kattni Rembor, Melissa LeBlanc-Williams
# and Tony DiCola, for Adafruit Industries.
# Original file created by Damien P. George </text>
#
# SPDX-License-Identifier: MIT

"""
`adafruit_framebuf`
====================================================

CircuitPython pure-python framebuf module, based on the micropython framebuf module.

Implementation Notes
--------------------

**Hardware:**

* `Adafruit SSD1306 OLED displays <https://www.adafruit.com/?q=ssd1306>`_
* `Adafruit HT16K33 Matrix displays <https://www.adafruit.com/?q=ht16k33>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_framebuf.git"

import os
import struct

# Framebuf format constants:
MVLSB = 0  # Single bit displays (like SSD1306 OLED)
MONO_VLSB = MVLSB  # Alias for MVLSB as used in micropython
RGB565 = 1  # 16-bit color displays
GS4_HMSB = 2  # Unimplemented!
MHMSB = 3  # Single bit displays like the Sharp Memory
MONO_HMSB = MHMSB  # Alias for MHMSB as used in micropython
RGB888 = 4  # Neopixels and Dotstars
GS2_HMSB = 5  # 2-bit color displays like the HT16K33 8x8 Matrix
# MONO_HLSB # Unimplemented!
# GS8 # Unimplemented!


class GS2HMSBFormat:
    """GS2HMSBFormat"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        pixel_num = (y * framebuf.stride + x)
        index = pixel_num >> 2
        pixel = framebuf.buf[index]
        shift = (pixel_num & 0b11) << 1
        mask = 0b11 << shift
        color = (color & 0b11) << shift
        framebuf.buf[index] = color | (pixel & (~mask))

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        pixel_num = (y * framebuf.stride + x)
        index = pixel_num >> 2
        pixel = framebuf.buf[index]
        shift = (pixel_num & 0b11) << 1
        return (pixel >> shift) & 0b11


    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            bits = color & 0b11
            fill = (bits << 6) | (bits << 4) | (bits << 2) | (bits << 0)
        else:
            fill = 0x00

        framebuf.buf = [fill for i in range(len(framebuf.buf))]

    @staticmethod
    def rect(framebuf, x, y, width, height, color):
        """Draw the outline of a rectangle at the given location, size and color."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                if _x in [x, x + width] or _y in [y, y + height]:
                    GS2HMSBFormat.set_pixel(framebuf, _x, _y, color)

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw the outline and interior of a rectangle at the given location, size and color."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                GS2HMSBFormat.set_pixel(framebuf, _x, _y, color)


class MHMSBFormat:
    """MHMSBFormat"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf.stride + x) // 8
        offset = 7 - x & 0x07
        framebuf.buf[index] = (framebuf.buf[index] & ~(0x01 << offset)) | (
                (color != 0) << offset
        )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf.stride + x) // 8
        offset = 7 - x & 0x07
        return (framebuf.buf[index] >> offset) & 0x01

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf.buf)):  # pylint: disable=consider-using-enumerate
            framebuf.buf[i] = fill

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        for _x in range(x, x + width):
            offset = 7 - _x & 0x07
            for _y in range(y, y + height):
                index = (_y * framebuf.stride + _x) // 8
                framebuf.buf[index] = (framebuf.buf[index] & ~(0x01 << offset)) | (
                        (color != 0) << offset
                )


class MVLSBFormat:
    """MVLSBFormat"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y >> 3) * framebuf.stride + x
        offset = y & 0x07
        framebuf.buf[index] = (framebuf.buf[index] & ~(0x01 << offset)) | (
                (color != 0) << offset
        )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y >> 3) * framebuf.stride + x
        offset = y & 0x07
        return (framebuf.buf[index] >> offset) & 0x01

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        if color:
            fill = 0xFF
        else:
            fill = 0x00
        for i in range(len(framebuf.buf)):  # pylint: disable=consider-using-enumerate
            framebuf.buf[i] = fill

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        while height > 0:
            index = (y >> 3) * framebuf.stride + x
            offset = y & 0x07
            for w_w in range(width):
                framebuf.buf[index + w_w] = (
                    framebuf.buf[index + w_w] & ~(0x01 << offset)
                    ) | ((color != 0) << offset)
            y += 1
            height -= 1


class RGB565Format:
    """
    This class implements the RGB565 format
    It assumes a little-endian byte order in the frame buffer
    """

    @staticmethod
    def color_to_rgb565(color):
        """Convert a color in either tuple or 24 bit integer form to RGB565,
        and return as two bytes"""
        if isinstance(color, tuple):
            hibyte = (color[0] & 0xF8) | (color[1] >> 5)
            lobyte = ((color[1] << 5) & 0xE0) | (color[2] >> 3)
        else:
            hibyte = ((color >> 16) & 0xF8) | ((color >> 13) & 0x07)
            lobyte = ((color >> 5) & 0xE0) | ((color >> 3) & 0x1F)
        return bytes([lobyte, hibyte])

    def set_pixel(self, framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf.stride + x) * 2
        framebuf.buf[index: index + 2] = self.color_to_rgb565(color)

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf.stride + x) * 2
        lobyte, hibyte = framebuf.buf[index: index + 2]
        r = hibyte & 0xF8
        g = ((hibyte & 0x07) << 5) | ((lobyte & 0xE0) >> 5)
        b = (lobyte & 0x1F) << 3
        return (r << 16) | (g << 8) | b

    def fill(self, framebuf, color):
        """completely fill/clear the buffer with a color"""
        rgb565_color = self.color_to_rgb565(color)
        for i in range(0, len(framebuf.buf), 2):
            framebuf.buf[i: i + 2] = rgb565_color

    def fill_rect(self, framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        rgb565_color = self.color_to_rgb565(color)
        for _y in range(2 * y, 2 * (y + height), 2):
            offset2 = _y * framebuf.stride
            for _x in range(2 * x, 2 * (x + width), 2):
                index = offset2 + _x
                framebuf.buf[index: index + 2] = rgb565_color


class RGB888Format:
    """RGB888Format"""

    @staticmethod
    def set_pixel(framebuf, x, y, color):
        """Set a given pixel to a color."""
        index = (y * framebuf.stride + x) * 3
        if isinstance(color, tuple):
            framebuf.buf[index: index + 3] = bytes(color)
        else:
            framebuf.buf[index: index + 3] = bytes(
                ((color >> 16) & 255, (color >> 8) & 255, color & 255)
            )

    @staticmethod
    def get_pixel(framebuf, x, y):
        """Get the color of a given pixel"""
        index = (y * framebuf.stride + x) * 3
        return (
                (framebuf.buf[index] << 16)
                | (framebuf.buf[index + 1] << 8)
                | framebuf.buf[index + 2]
        )

    @staticmethod
    def fill(framebuf, color):
        """completely fill/clear the buffer with a color"""
        fill = (color >> 16) & 255, (color >> 8) & 255, color & 255
        for i in range(0, len(framebuf.buf), 3):
            framebuf.buf[i: i + 3] = bytes(fill)

    @staticmethod
    def fill_rect(framebuf, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments
        fill = (color >> 16) & 255, (color >> 8) & 255, color & 255
        for _x in range(x, x + width):
            for _y in range(y, y + height):
                index = (_y * framebuf.stride + _x) * 3
                framebuf.buf[index: index + 3] = bytes(fill)


class FrameBuffer:
    """FrameBuffer object.

    :param buf: An object with a buffer protocol which must be large enough to contain every
                pixel defined by the width, height and format of the FrameBuffer.
    :param width: The width of the FrameBuffer in pixel
    :param height: The height of the FrameBuffer in pixel
    :param buf_format: Specifies the type of pixel used in the FrameBuffer; permissible values
                        are listed under Constants below. These set the number of bits used to
                        encode a color value and the layout of these bits in ``buf``. Where a
                        color value c is passed to a method, c is  a small integer with an encoding
                        that is dependent on the format of the FrameBuffer.
    :param stride: The number of pixels between each horizontal line of pixels in the
                   FrameBuffer. This defaults to ``width`` but may need adjustments when
                   implementing a FrameBuffer within another larger FrameBuffer or screen. The
                   ``buf`` size must accommodate an increased step size.

    """

    

    def __init__(self, buf, width, height, buf_format=MVLSB, stride=None):
        # pylint: disable=too-many-arguments
        self.buf = buf
        self.width = width
        self.height = height
        self.stride = stride
        self._font = None
        if self.stride is None:
            self.stride = width

        format_lookup = {
            MVLSB: MVLSBFormat,
            MHMSB: MHMSBFormat,
            RGB888: RGB888Format,
            RGB565: RGB565Format,
            GS2_HMSB: GS2HMSBFormat,
        }
        try:
            self.format = format_lookup[buf_format]()
        except KeyError:
            raise ValueError(f"Invalid buffer format: {buf_format}")
        self._rotation = 0

    @property
    def display_width(self):
        if self.rotation in (1, 3):
            return self.height
        return self.width

    @property
    def display_height(self):
        if self.rotation in (1, 3):
            return self.width
        return self.height
    
    @property
    def rotation(self):
        """The rotation setting of the display, can be one of (0, 1, 2, 3)"""
        return self._rotation

    @rotation.setter
    def rotation(self, val):
        if not val in (0, 1, 2, 3):
            raise RuntimeError("Bad rotation setting")
        self._rotation = val

    def fill(self, color):
        """Fill the entire FrameBuffer with the specified color."""
        self.format.fill(self, color)

    def fill_rect(self, x, y, width, height, color):
        """Draw a rectangle at the given location, size and color. The ``fill_rect`` method draws
        both the outline and interior."""
        # pylint: disable=too-many-arguments, too-many-boolean-expressions
        self.rect(x, y, width, height, color, fill=True)

    def pixel(self, x, y, color=None):
        """If ``color`` is not given, get the color value of the specified pixel. If ``color`` is
        given, set the specified pixel to the given color."""
        if self.rotation == 1:
            x, y = y, x
            x = self.width - x - 1
        if self.rotation == 2:
            x = self.width - x - 1
            y = self.height - y - 1
        if self.rotation == 3:
            x, y = y, x
            y = self.height - y - 1

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        if color is None:
            return self.format.get_pixel(self, x, y)
        self.format.set_pixel(self, x, y, color)
        return None

    def hline(self, x, y, width, color):
        """Draw a horizontal line up to a given length."""
        self.rect(x, y, width, 1, color, fill=True)

    def vline(self, x, y, height, color):
        """Draw a vertical line up to a given length."""
        self.rect(x, y, 1, height, color, fill=True)

    def circle(self, center_x, center_y, radius, color):
        """Draw a circle at the given midpoint location, radius and color.
        The ```circle``` method draws only a 1 pixel outline."""
        x = radius - 1
        y = 0
        d_x = 1
        d_y = 1
        err = d_x - (radius << 1)
        while x >= y:
            self.pixel(center_x + x, center_y + y, color)
            self.pixel(center_x + y, center_y + x, color)
            self.pixel(center_x - y, center_y + x, color)
            self.pixel(center_x - x, center_y + y, color)
            self.pixel(center_x - x, center_y - y, color)
            self.pixel(center_x - y, center_y - x, color)
            self.pixel(center_x + y, center_y - x, color)
            self.pixel(center_x + x, center_y - y, color)
            if err <= 0:
                y += 1
                err += d_y
                d_y += 2
            if err > 0:
                x -= 1
                d_x += 2
                err += d_x - (radius << 1)

    def rect(self, x, y, width, height, color, *, fill=False):
        """Draw a rectangle at the given location, size and color. The ```rect``` method draws only
        a 1 pixel outline."""
        # pylint: disable=too-many-arguments
        if self.rotation == 1:
            x, y = y, x
            width, height = height, width
            x = self.width - x - width
        if self.rotation == 2:
            x = self.width - x - width
            y = self.height - y - height
        if self.rotation == 3:
            x, y = y, x
            width, height = height, width
            y = self.height - y - height

        # pylint: disable=too-many-boolean-expressions
        if (
                width < 1
                or height < 1
                or (x + width) <= 0
                or (y + height) <= 0
                or y >= self.height
                or x >= self.width
        ):
            return
        x_end = min(self.width - 1, x + width - 1)
        y_end = min(self.height - 1, y + height - 1)
        x = max(x, 0)
        y = max(y, 0)
        if fill:
            self.format.fill_rect(self, x, y, x_end - x + 1, y_end - y + 1, color)
        else:
            self.format.fill_rect(self, x, y, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x, y, 1, y_end - y + 1, color)
            self.format.fill_rect(self, x, y_end, x_end - x + 1, 1, color)
            self.format.fill_rect(self, x_end, y, 1, y_end - y + 1, color)

    def line(self, x_0, y_0, x_1, y_1, color):
        # pylint: disable=too-many-arguments
        """Bresenham's line algorithm"""
        d_x = abs(x_1 - x_0)
        d_y = abs(y_1 - y_0)
        x, y = x_0, y_0
        s_x = -1 if x_0 > x_1 else 1
        s_y = -1 if y_0 > y_1 else 1
        if d_x > d_y:
            err = d_x / 2.0
            while x != x_1:
                self.pixel(x, y, color)
                err -= d_y
                if err < 0:
                    y += s_y
                    err += d_x
                x += s_x
        else:
            err = d_y / 2.0
            while y != y_1:
                self.pixel(x, y, color)
                err -= d_x
                if err < 0:
                    x += s_x
                    err += d_y
                y += s_y
        self.pixel(x, y, color)

    def blit(self):
        """blit is not yet implemented"""
        raise NotImplementedError()

    def scroll(self, delta_x, delta_y):
        """shifts framebuf in x and y direction"""
        if delta_x < 0:
            shift_x = 0
            xend = self.width + delta_x
            dt_x = 1
        else:
            shift_x = self.width - 1
            xend = delta_x - 1
            dt_x = -1
        if delta_y < 0:
            y = 0
            yend = self.height + delta_y
            dt_y = 1
        else:
            y = self.height - 1
            yend = delta_y - 1
            dt_y = -1
        while y != yend:
            x = shift_x
            while x != xend:
                self.format.set_pixel(
                    self, x, y, self.format.get_pixel(self, x - delta_x, y - delta_y)
                )
                x += dt_x
            y += dt_y

    # pylint: disable=too-many-arguments
    def text(self, string, x, y, color, *, font_name="font5x8.bin", size=1):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        # determine our effective width/height, taking rotation into account
        frame_width = self.width
        frame_height = self.height
        if self.rotation in (1, 3):
            frame_width, frame_height = frame_height, frame_width

        for chunk in string.split("\n"):
            if not self._font or self._font.font_name != font_name:
                # load the font!
                self._font = BitmapFont(font_name)
            width = self._font.font_width
            height = self._font.font_height
            for i, char in enumerate(chunk):
                char_x = x + (i * (width + 1)) * size
                if (
                        char_x + (width * size) > 0
                        and char_x < frame_width
                        and y + (height * size) > 0
                        and y < frame_height
                ):
                    self._font.draw_char(char, char_x, y, self, color, size=size)
            y += height * size

    # pylint: enable=too-many-arguments

    def image(self, img):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size."""
        # determine our effective width/height, taking rotation into account
        width = self.width
        height = self.height
        if self.rotation in (1, 3):
            width, height = height, width

        if isinstance(self.format, (RGB565Format, RGB888Format)) and img.mode != "RGB":
            raise ValueError("Image must be in mode RGB.")
        if isinstance(self.format, (MHMSBFormat, MVLSBFormat)) and img.mode != "1":
            raise ValueError("Image must be in mode 1.")

        imwidth, imheight = img.size
        if imwidth != width or imheight != height:
            raise ValueError(
                f"Image must be same dimensions as display ({width}x{height})."
            )
        # Grab all the pixels from the image, faster than getpixel.
        pixels = img.load()
        # Clear buffer
        for i in range(len(self.buf)):  # pylint: disable=consider-using-enumerate
            self.buf[i] = 0
        # Iterate through the pixels
        for x in range(width):  # yes this double loop is slow,
            for y in range(height):  # but these displays are small!
                if img.mode == "RGB":
                    self.pixel(x, y, pixels[(x, y)])
                elif pixels[(x, y)]:
                    self.pixel(x, y, 1)  # only write if pixel is true


    # MicroPython framebuffer ellipse.
    # Author: Damien P. George
    # License: MIT License (https://opensource.org/licenses/MIT)
    # Source: https://github.com/micropython/micropython/blob/master/extmod/modframebuf.c
    def ellipse(self, x, y, xr, yr, c, f=False, m=None):
        """
        Draw an ellipse at the given location. Radii xr and yr define the geometry; equal values cause a circle to be drawn.
        The c parameter defines the color.
        The optional f parameter can be set to True to fill the ellipse. Otherwise just a one pixel outline is drawn.
        The optional m parameter enables drawing to be restricted to certain quadrants of the ellipse.
        The LS four bits determine which quadrants are to be drawn, with bit 0 specifying Q1, b1 Q2, b2 Q3 and b3 Q4.
        Quadrants are numbered counterclockwise with Q1 being top right.

        x: x center
        y: y center
        xr: x radius
        yr: y radius
        c: color
        f: fill
        m: quadrants
        """
        ELLIPSE_MASK_FILL = 0x10
        ELLIPSE_MASK_ALL = 0x0f
        ELLIPSE_MASK_Q1 = 0x01
        ELLIPSE_MASK_Q2 = 0x02
        ELLIPSE_MASK_Q3 = 0x04
        ELLIPSE_MASK_Q4 = 0x08

        def draw_ellipse_points(fb, cx, cy, x_counter, y_counter, col, mask):
            if (mask & ELLIPSE_MASK_FILL):
                if (mask & ELLIPSE_MASK_Q1):
                    fb.fill_rect(cx, cy - y_counter, x_counter + 1, 1, col)
                if (mask & ELLIPSE_MASK_Q2):
                    fb.fill_rect(cx - x_counter, cy - y_counter, x_counter + 1, 1, col)
                if (mask & ELLIPSE_MASK_Q3):
                    fb.fill_rect(cx - x_counter, cy + y_counter, x_counter + 1, 1, col)
                if (mask & ELLIPSE_MASK_Q4):
                    fb.fill_rect(cx, cy + y_counter, x_counter + 1, 1, col)
            else:
                if mask & ELLIPSE_MASK_Q1:
                    fb.pixel(cx + x_counter, cy - y_counter, col)
                if mask & ELLIPSE_MASK_Q2:
                    fb.pixel(cx - x_counter, cy - y_counter, col)
                if mask & ELLIPSE_MASK_Q3:
                    fb.pixel(cx - x_counter, cy + y_counter, col)
                if mask & ELLIPSE_MASK_Q4:
                    fb.pixel(cx + x_counter, cy + y_counter, col)

        mask = ELLIPSE_MASK_FILL if f else 0
        if m is not None:
            mask |= m & ELLIPSE_MASK_ALL
        else:
            mask |= ELLIPSE_MASK_ALL

        if (xr == 0 & yr == 0):
            if mask & ELLIPSE_MASK_ALL:
                self.pixel(x, y, c)
            return

        two_asquare = 2 * xr * xr
        two_bsquare = 2 * yr * yr
        x_counter = xr
        y_counter = 0
        xchange = yr * yr * (1 - 2 * xr)
        ychange = xr * xr
        ellipse_error = 0
        stoppingx = two_bsquare * xr
        stoppingy = 0

        while (stoppingx >= stoppingy):  # 1st set of points,  y' > -1
            draw_ellipse_points(self, x, y, x_counter, y_counter, c, mask)
            y_counter += 1
            stoppingy += two_asquare
            ellipse_error += ychange
            ychange += two_asquare
            if ((2 * ellipse_error + xchange) > 0):
                x_counter -= 1
                stoppingx -= two_bsquare
                ellipse_error += xchange
                xchange += two_bsquare
        # 1st point set is done start the 2nd set of points
        x_counter = 0
        y_counter = yr
        xchange = yr * yr
        ychange = xr * xr * (1 - 2 * yr)
        ellipse_error = 0
        stoppingx = 0
        stoppingy = two_asquare * yr
        while (stoppingx <= stoppingy):  # // 2nd set of points, y' < -1
            draw_ellipse_points(self, x, y, x_counter, y_counter, c, mask)
            x_counter += 1
            stoppingx += two_bsquare
            ellipse_error += xchange
            xchange += two_bsquare
            if ((2 * ellipse_error + ychange) > 0):
                y_counter -= 1
                stoppingy -= two_asquare
                ellipse_error += ychange
                ychange += two_asquare




# MicroPython basic bitmap font renderer.
# Author: Tony DiCola
# License: MIT License (https://opensource.org/licenses/MIT)
class BitmapFont:
    """A helper class to read binary font tiles and 'seek' through them as a
    file to display in a framebuffer. We use file access so we dont waste 1KB
    of RAM on a font!"""

    def __init__(self, font_name="font5x8.bin"):
        # Specify the drawing area width and height, and the pixel function to
        # call when drawing pixels (should take an x and y param at least).
        # Optionally specify font_name to override the font file to use (default
        # is font5x8.bin).  The font format is a binary file with the following
        # format:
        # - 1 unsigned byte: font character width in pixels
        # - 1 unsigned byte: font character height in pixels
        # - x bytes: font data, in ASCII order covering all 255 characters.
        #            Each character should have a byte for each pixel column of
        #            data (i.e. a 5x8 font has 5 bytes per character).
        self.font_name = font_name

        # Open the font file and grab the character width and height values.
        # Note that only fonts up to 8 pixels tall are currently supported.
        try:
            self._font = open(  # pylint: disable=consider-using-with
                self.font_name, "rb"
            )
            self.font_width, self.font_height = struct.unpack("BB", self._font.read(2))
            # simple font file validation check based on expected file size
            if 2 + 256 * self.font_width != os.stat(font_name)[6]:
                raise RuntimeError("Invalid font file: " + font_name)
        except OSError:
            print("Could not find font file", font_name)
            raise
        except OverflowError:
            # os.stat can throw this on boards without long int support
            # just hope the font file is valid and press on
            pass

    def deinit(self):
        """Close the font file as cleanup."""
        self._font.close()

    def __enter__(self):
        """Initialize/open the font file"""
        self.__init__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """cleanup on exit"""
        self.deinit()

    def draw_char(
            self, char, x, y, framebuffer, color, size=1
    ):  # pylint: disable=too-many-arguments
        """Draw one character at position (x,y) to a framebuffer in a given color"""
        size = max(size, 1)
        # Don't draw the character if it will be clipped off the visible area.
        # if x < -self.font_width or x >= framebuffer.width or \
        #   y < -self.font_height or y >= framebuffer.height:
        #    return
        # Go through each column of the character.
        for char_x in range(self.font_width):
            # Grab the byte for the current column of font data.
            self._font.seek(2 + (ord(char) * self.font_width) + char_x)
            try:
                line = struct.unpack("B", self._font.read(1))[0]
            except RuntimeError:
                continue  # maybe character isnt there? go to next
            # Go through each row in the column byte.
            for char_y in range(self.font_height):
                # Draw a pixel for each bit that's flipped on.
                if (line >> char_y) & 0x1:
                    framebuffer.fill_rect(
                        x + char_x * size, y + char_y * size, size, size, color
                    )

    def width(self, text):
        """Return the pixel width of the specified text message."""
        return len(text) * (self.font_width + 1)


class FrameBuffer1(FrameBuffer):  # pylint: disable=abstract-method
    """FrameBuffer1 object. Inherits from FrameBuffer."""