import framebuf


def run():
    height = 8
    width = 16
    rotate = True
    
    if rotate:
        height, width = width, height
        mode = framebuf.GS2_HMSB
    else:
        mode = framebuf.GS2_HMSB
    bufferlen = ((height * width * 2) // 8)
    buffer = bytearray(bufferlen)
    memview = memoryview(buffer)
    inverse_buffer = bytearray(2)
    
    fb = framebuf.FrameBuffer(buffer, height, width, mode)
    
    #fb.vline(5,0,4,3)
    #fb.vline(0,0,4,2)
    WHITE = 3
    RED = 2
    BLACK = 1
    
    fb.fill(WHITE)
    fb.hline(0,1,6,BLACK) # Black
    fb.hline(0,3,6,RED) # Red
    fb.vline(3,0,6,WHITE) # White
    
    if False:
        patterns = (0b0011, 0b0101)
        for p in patterns:
            foobar(inverse_buffer, buffer, memview, p)
            print()
    # print_bsend(inverse_buffer, memview, buffer)
    print_raw2(buffer, width)
    
    
@micropython.viper
def _lmap(dest: ptr8, source: ptr8, pattern: int, length: int):
    d: int = 0  # dest index
    s: int = 0  # Source index
    e: int = 0  # Current output byte (8 pixels of 1 bit
    t: int = 0  # Current input byte (4 pixels of 2 bits)
    while d < length:  # For each byte of o/p
        e = 0
        # Two sets of 4 pixels
        for _ in range(2):
            t = source[s]
            for _ in range(4):
                e |= (pattern >> (t & 3)) & 1
                t >>= 2
                e <<= 1
            s += 1

        dest[d] = e >> 1
        d += 1
        
        
def foobar(inverse_buffer, buffer, mvb, pattern):
    fbidx = 0  # Index into framebuf
    nbytes = len(inverse_buffer)  # Bytes to send
    didx = nbytes * 2  # Increment of framebuf index
    nleft = len(buffer)  # Size of framebuf
    while nleft > 0:
        _lmap(inverse_buffer, mvb[fbidx:], pattern, nbytes)
        for b in (inverse_buffer):
            print(f"{b:08b}")
        fbidx += didx  # Adjust for bytes already sent.
        nleft -= didx  # Could be < 0 if framebuf size not divisible by ibuf size
        nbytes = min(nbytes, nleft)  # but iteration will stop
    
    
def print_bsend(inverse_buffer,memview, buffer):
    fbidx = 0  # Index into framebuf
    nbytes = len(inverse_buffer)  # Bytes to send
    nleft = len(buffer)  # Size of framebuf
    npass = 0
    while nleft > 0:
        bsend(inverse_buffer, memview, fbidx, nbytes)  # Invert, buffer and send nbytes
        fbidx += nbytes  # Adjust for bytes already sent
        nleft -= nbytes
        nbytes = min(nbytes, nleft)
        if not ((npass := npass + 1) % 16):
            pass
       

        
def print_raw(buffer, w):
    for i, b in enumerate(buffer):
        if i % (w//8) == 0:
            print()
        print(f"{b:08b}", end=' ')
        
def print_raw2(buffer, w):
    cmap={
        ('11'): '.',
        ('01'): 'r',
        ('10'): 'B',
        ('00'): 'X',
        }
    for i, b in enumerate(buffer):
        if i % (w // 8) == 0:
            print()
        s = ''.join(reversed(f"{b:08b}"))
        print(''.join([cmap[s[i:i+2]] for i in range(0,8,2) ]), end=' ')
        
# Invert: EPD is black on white
# 337/141 us for 2000 bytes (125/250MHz)
@micropython.viper
def _linv(dest: ptr32, source: ptr32, length: int):
    n: int = length - 1
    z: uint32 = int(0xFFFFFFFF)
    while n >= 0:
        dest[n] = source[n] ^ z
        n -= 1
        
@micropython.native
def bsend(inverse_buffer, memview, start, nbytes):  # Invert b<->w, buffer and send nbytes source bytes
    _linv(inverse_buffer, memview[start:], nbytes >> 2)
    
    for i, b in enumerate(inverse_buffer):
        if i % 2 == 0:
            print()
        print(f"{b:08b}", end=' ')
    print('|', end='')
    

        
if __name__ == '__main__':
    run()