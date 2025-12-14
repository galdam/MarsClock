import os
import struct

DEFAULT_FONT_DIR = f"{__file__.rsplit('/', 1)[0]}" #'/upydrivers/display/font' #__file__.rsplit('/', 1)[0]
V_SPACING=0
H_SPACING=1

class BitmapFont:
    """A helper class to read binary font tiles and 'seek' through them as a
    file to display in a framebuffer. We use file access so we dont waste 1KB
    of RAM on a font!"""

    def __init__(self, font_name=None, font_dir=None):
        self.font_name = "font_adafruit_8x8.bin" if font_name is None else font_name
        if font_dir is None:
            font_dir = DEFAULT_FONT_DIR
        self.font_path = '/'.join([font_dir, self.font_name])

        # print("Loading font file", self.font_path)
        # Open the font file and grab the character width and height values.
        try:
            self._font_fh = open(  # pylint: disable=consider-using-with
                self.font_path, "rb")
            # Unpack the font header
            (self.font_width, self.font_height, 
             self.min_char, self.max_char, 
             self.is_varwidth) = struct.unpack("BBBBB", self._font_fh.read(5))
            
            # Number of bytes of image data for the character
            self.nbytes_width = ((self.font_width-1) // 8)+1
            # Variable width fonts use an extra byte for the width
            self.nbytes_char = self.is_varwidth + (self.nbytes_width * self.font_height)
            self.n_chars = (self.max_char+1)-self.min_char
            # simple font file validation check based on expected file size
            expected_size = 5 + (self.nbytes_char * self.n_chars)
            if expected_size != os.stat(self.font_path)[6]:
                print("Invalid font file: {}. Expected size: {}".format(self.font_path, expected_size))
        except OSError as err:
            print("[BitmapFont] ERROR: Could not find font file", self.font_path)
            raise err
        except OverflowError:
            # os.stat can throw this on boards without long int support
            # just hope the font file is valid and press on
            pass
        except Exception as err:
            print("[BitmapFont] ERROR: Error loading font file", self.font_path)
            raise err

    def _char_start(self, char):
        """Find the location in the file where the character data starts"""
        char_num = ord(char)
        if not (self.min_char <= char_num <= self.max_char):
            print(f'Character not in range: {char_num}')
            return None
        return 5 + (char_num - self.min_char) * (self.nbytes_char)

    def _read_char(self, char):
        """
        Read the character data
        Return: character width, pixel data
        """
        # Find the start of the character
        char_start = self._char_start(char)

        # If the character is out of range, just leave a space
        if char_start is None:
            return self.font_width, [0]*(self.nbytes_width*self.font_height)
        
        # Seek to the start of the character and read
        self._font_fh.seek(char_start)
        b = struct.unpack("B"*self.nbytes_char, self._font_fh.read(self.nbytes_char))

        # Return the width and the data
        if self.is_varwidth:
            return b[0], b[1:]
        else:
            return self.font_width, b
        
    def _char_width(self, char):
        if not self.is_varwidth:
            return self.font_width
        
        char_start = self._char_start(char)
        if char_start is None:
            return self.font_width
        
        self._font_fh.seek(char_start)
        return struct.unpack("B", self._font_fh.read(1))[0]
    
    def deinit(self):
        """Close the font file as cleanup."""
        self._font_fh.close()

    def __enter__(self):
        """Initialize/open the font file"""
        self.__init__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """cleanup on exit"""
        self.deinit()        

    def text_width(self, text, h_spacing=None, size=1):
        """Return the pixel width of the specified text message"""
        h_spacing = H_SPACING if h_spacing is None else h_spacing
        
        if '\n' in text:
            raise ValueError('"text_width" is invalid for strings containing line breaks, use "text_dim" instead.')
        if not self.is_varwidth:
            return len(text) * (self.font_width * size) + ((len(text)-1) * h_spacing)
        else:
            return sum([self._char_width(c) * size for c in text]) + ((len(text)-1) * h_spacing)
        
    def text_height(self, text, size=1):
        """Return the pixel height of the specified text message."""   
        if '\n' in text:
            raise ValueError('"text_height" is invalid for strings containing line breaks, use "text_dim" instead.')
        return (self.font_height*size)
    
    def text_dim(self, text, h_spacing=None, v_spacing=None, size=1):
        """The width and height of the string with the specified spacing parameters."""
        h_spacing = H_SPACING if h_spacing is None else h_spacing
        v_spacing = V_SPACING if v_spacing is None else v_spacing

        lines = text.split('\n')
        width = max([self.text_width(l, h_spacing, size) for l in lines])
        height = (self.text_height('', size) * len(lines)) + ((len(lines)-1) * v_spacing)
        return width, height

    def draw_char(self, fb, char, x, y, color, size=1):  
        """
        Draw one character at position (x,y) to a framebuffer in a given color
        
        """
        size = max(size, 1)
        # Don't draw the character if it will be clipped off the visible area.
        # if x < -self.font_width or x >= framebuffer.width or \
        #   y < -self.font_height or y >= framebuffer.height:
        #    return
        # Go through each column of the character.

        width, char_bytes = self._read_char(char)
        for char_y in range(self.font_height):
            for char_x in range(width):
                line = char_bytes[(char_y*self.nbytes_width)+ (char_x // 8)]
                if line >> (7 - (char_x % 8)) & 0x1:
                    fb.fill_rect(x + char_x * size, y + char_y * size, size, size, color)
        return width

    def draw_text(self, fb, s, x, y, color, h_spacing=None, v_spacing=None, size=None,):
        """Place text on the screen in variables sizes. Breaks on \n to next line.

        Does not break on line going off screen.
        """
        h_spacing= H_SPACING if h_spacing is None else h_spacing
        v_spacing= V_SPACING if v_spacing is None else v_spacing
        size = 1 if size is None else max([1, size])

        for chunk in s.split("\n"):
            # width = self._font.font_width
            height = self.font_height
            char_x = x
            for char in chunk:
                if (0 < char_x < fb.width and 0 < y < fb.height):
                    char_x += self.draw_char(fb, char, char_x, y, color, size) + h_spacing
            y += (height * size) + v_spacing
