import math
from upydrivers import upylog

# TODO Clean this up, look at using the micropython native functions


def msb_iterator(buffer, width, height, rotation, deinterlace):
    byte = 0
    bit_count = 0
    for x, y in pixel_location_iterator(width, height, rotation):
        pix = get_msb_pixel(buffer, x, y, width)
        bit = pix >> deinterlace & 1
        byte |= (bit << bit_count)

        if bit_count == 7:
            yield byte
            byte = 0
            bit_count = 0
        else:
            bit_count += 1
    if bit_count != 0:
        yield byte


def deinterlace_bytearray(src_bytearray, byteix, inverse=False):
    upylog.trace('[byteops.deinterlace_bytearray]')
    for i in range(0, len(src_bytearray), 2):
        yield deinterlace_bytepair(src_bytearray[i:i+2], byteix, inverse)


def deinterlace_bytepair(src_bytes, byteix, inverse=False):
    """
    Based on the '_lmap' code from:
    https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/pico_epaper_42.py
    My experience with bit operations is pretty limited,
    so I've just inverted  the inversion.
    """
    if len(src_bytes) > 2:
        raise ValueError(f"Too many bytes to de-interlace: {len(src_bytes)}")
    pattern = (0b0011, 0b0101)[byteix]
    dst_byte = 0b0
    for src_byte in src_bytes:
        for _ in range(4):
            dst_byte |= (pattern >> (src_byte & 3)) & 1
            src_byte >>= 2
            dst_byte <<= 1
    dst_byte = dst_byte >> 1
    if not inverse:
        dst_byte = dst_byte ^ 0xFF
    return rbit8(dst_byte)


def rotate_bytearray_clockwise(src_bytearray, width, height):
    # height = (len(src_bytearray) * 8) // width
    # Iterate the columns of bytes in the buffer
    for col_byte in range(math.ceil(width / 8)):
        # Iterate the position in the input byte (right to left)
        for bit_pos_in in range(7, -1, -1):
            for row_byte in range(math.ceil((height / 8)) - 1, -1, -1):
                byte = 0
                for row_bit in range(7, -1, -1):
                    loc = (((row_byte * 8) + row_bit) * math.ceil(width / 8)) + col_byte
                    byte_in = src_bytearray[loc]
                    bit = (byte_in >> (7 - bit_pos_in) & 1)
                    byte |= (bit << row_bit)
                yield byte


def rotate_bytearray_anticlockwise(src_bytearray, width, height):
    """
    Rotate and byte array of mono MSB.
    """
    #height = (len(src_bytearray) * 8) // width
    # Iterate the columns of bytes in the buffer
    for col_byte in range(math.ceil(width / 8) - 1, -1, -1):
        # Iterate the position in the input byte (right to left)
        for bit_pos_in in range(8):
            # for row_byte in range((height//8)-1, -1, -1):
            for row_byte in range(math.ceil(height / 8)):
                byte = 0
                for row_bit in range(8):
                    loc = (((row_byte * 8) + row_bit) * math.ceil(width / 8)) + col_byte
                    byte_in = src_bytearray[loc]
                    bit = (byte_in >> (7 - bit_pos_in) & 1)
                    byte |= (bit << row_bit)
                yield byte


def rotate_msb_bytearray(src_bytearray, width, height, rotation):
    if rotation == 0:
        upylog.trace('[byteops.rotate_msb_bytearray] Rotation 0, reversing MSB to LSB')
        for b in src_bytearray:
            yield rbit8(b)
    elif rotation == 1:
        upylog.trace('[byteops.rotate_msb_bytearray] Rotation 1, rotate_bytearray_clockwise')
        for b in rotate_bytearray_clockwise(src_bytearray, width, height):
            yield b
    elif rotation == 2:
        upylog.trace('[byteops.rotate_msb_bytearray] Rotation 2, returning bytes in reverse, MSB inherently becomes LSB')
        for b in reversed(src_bytearray):
            yield b
    elif rotation == 3:
        upylog.trace('[byteops.rotate_msb_bytearray] Rotation 3, rotate_bytearray_anticlockwise')
        for b in rotate_bytearray_anticlockwise(src_bytearray, width, height):
            yield rbit8(b)


def pixel_location_iterator(width, height, rotation=0):
    if rotation == 0:
        for y in range(height):
            for x in range(width):
                yield x, y
    elif rotation == 1:
        for x in range(width-1, -1, -1):
            for y in range(height):
                yield x, y
    elif rotation == 2:
        for y in range(height-1, -1, -1):
            for x in range(width-1, -1, -1):
                yield x, y
    elif rotation == 3:
        for x in range(width):
            for y in range(height-1, -1, -1):
                yield x, y
                

def get_msb_pixel(buffer_arr, x, y, width):
    """Get the color of a given pixel"""
    pixel_num = (y * width + x)
    index = pixel_num >> 2
    pixel = buffer_arr[index]
    shift = (pixel_num & 0b11) << 1
    return (pixel >> shift) & 0b11


# Bit reverse an 8 bit value
def rbit8(v):
    v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
    v = (v & 0x33) << 2 | (v & 0xcc) >> 2
    return (v & 0x55) << 1 | (v & 0xaa) >> 1

__ = '''
def rotate_bytearray_90_clockwise(src_bytearray, width):
    """Main function to rotate a byte array representing a bit matrix by 90 degrees clockwise."""
    bit_matrix = byte_array_to_bit_matrix(src_bytearray, width)
    rotated_matrix = rotate_matrix_90_clockwise(bit_matrix)
    rotated_bytearray = bit_matrix_to_byte_array(rotated_matrix)
    for b in rotated_bytearray:
        yield b

def byte_array_to_bit_matrix(byte_array, cols):
    """Converts a byte array into a 2D matrix of bits."""
    bit_matrix = []
    bit_count = len(byte_array) * 8  # rows * cols

    # Convert byte array into a list of bits
    bits = []
    for byte in byte_array:
        # Extract each bit from the byte
        # bits.extend([(byte >> i) & 1 for i in range(7, -1, -1)])
        # bits.extend([(byte >> (7 - i)) & 1 for i in range(8)])
        bits.extend([(byte >> (7 - i)) & 1 for i in range(7, -1, -1)])

    # Trim the bits to the required number of rows * cols
    bits = bits[:bit_count]  # TODO Remove?
    # Create the matrix
    for i in range(0, bit_count, cols):
        bit_matrix.append(bits[i:i + cols])
    return bit_matrix


def rotate_matrix_90_clockwise(matrix):
    """Rotates a matrix 90 degrees clockwise."""
    rows = len(matrix)
    cols = len(matrix[0])
    rotated_matrix = [[0] * rows for _ in range(cols)]

    for r in range(rows):
        for c in range(cols):
            rotated_matrix[c][rows - 1 - r] = matrix[r][c]

    return rotated_matrix


def bit_matrix_to_byte_array(bit_matrix):
    """Converts a 2D bit matrix back into a byte array."""
    rows = len(bit_matrix)
    cols = len(bit_matrix[0])

    # Flatten the matrix into a list of bits
    bits = [bit for row in bit_matrix for bit in row]

    # Group bits into bytes (8 bits per byte)
    byte_array = []
    for i in range(0, len(bits), 8):
        byte = 0
        # Reconstitute with MSB
        for bit_pos, bit in enumerate(reversed(bits[i:i + 8])):
            byte |= (bit << (7 - bit_pos))
        byte_array.append(byte)
    return bytearray(byte_array)
    
'''






