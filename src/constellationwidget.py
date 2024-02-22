import ujson as json

CK = 0
CW = 1

def draw_star_chart(epd, start, constellation):
    x0, y0 = start
    chart = json.load(open(f'data/starcharts/{constellation}.json'))
    for a, b in chart['links']:
        (x1, y1), (x2, y2) = chart['stars'][a], chart['stars'][b]
        epd.line(x0+x1, y0+y1, x0+x2, y0+y2, CK)
    r0 = 3
    r1 = r0+2
    # Erase the border around the stars
    for n, (x, y) in chart['stars'].items():
        if not n.startswith('OFF'):
            epd.ellipse(x0+x, y0+y, r1, r1, CW, True)
    # Draw the stars
    for n, (x, y) in chart['stars'].items():
        if not n.startswith('OFF'):
            epd.ellipse(x0+x, y0+y, r0, r0, CK, True)
    
    for m, x, y in chart['annotations']:
        epd.text(m, x0+x, y0+y, CK)
    for m, x,y in chart['titles']:
        epd.text(m, x0+x, y0+y, CK)