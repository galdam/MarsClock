import pytest

from marsclock.astro import daylength
from marsclock.astro.astrotime import EarthDateTime, HOUR, MINUTE

CAMBRIDGE = (52.205276, 0.119167)
COVENTRY = (52.408054, -1.510556)
ABERDEEN = (57.149651, -2.099075)
PARIS = (48.8575, 2.3514)

__ =[
    [(2025, 1, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((8, 8), (15, 57))],
    [(2025, 2, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((7, 39), (16, 47))],
    [(2025, 3, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((6, 45), (17, 39))],
    [(2025, 4, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((6, 33), (19, 33))],
    [(2025, 5, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((5, 28), (20, 25))],
    [(2025, 6, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((4, 44), (21, 11))],
    [(2025, 7, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((4, 42), (21, 23))],
    [(2025, 8, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((5, 20), (20, 49))],  # 128
    [(2025, 9, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((6, 11), (19, 46))],  # 146
    [(2025, 10, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((7, 0), (18, 36))],
    [(2025, 11, 1, 0, 0, 0, 'GMT'), CAMBRIDGE, ((6, 55), (16, 30))],

    [(2025, 1, 1, 0, 0, 0, 'GMT'), COVENTRY, ((8, 16), (16, 3))],
    [(2025, 2, 1, 0, 0, 0, 'GMT'), COVENTRY, ((7, 46), (16, 54))],  # 133
    [(2025, 3, 1, 0, 0, 0, 'GMT'), COVENTRY, ((6, 51), (17, 45))],
    [(2025, 4, 1, 0, 0, 0, 'GMT'), COVENTRY, ((6, 40), (19, 40))],
    [(2025, 5, 1, 0, 0, 0, 'GMT'), COVENTRY, ((5, 34), (20, 32))],
    [(2025, 6, 1, 0, 0, 0, 'GMT'), COVENTRY, ((4, 49), (21, 18))],
    [(2025, 7, 1, 0, 0, 0, 'GMT'), COVENTRY, ((4, 48), (21, 31))],
    [(2025, 8, 1, 0, 0, 0, 'GMT'), COVENTRY, ((5, 26), (20, 57))],
    [(2025, 9, 1, 0, 0, 0, 'GMT'), COVENTRY, ((6, 17), (19, 53))],  # 137
    [(2025, 10, 1, 0, 0, 0, 'GMT'), COVENTRY, ((7, 7), (18, 42))],  # 139
    [(2025, 11, 1, 0, 0, 0, 'GMT'), COVENTRY, ((7, 2), (16, 36))],
]

@pytest.mark.parametrize("et,coord,exp", [

    [(2025, 1, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((8, 47), (15, 37))],
    [(2025, 2, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((8, 7), (16, 37))],
    [(2025, 3, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((7, 1), (17, 41))],
    [(2025, 4, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((6, 37), (19, 48))],
    [(2025, 5, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((5, 19), (20, 53))],
    [(2025, 6, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((4, 21), (21, 51))],
    [(2025, 7, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((4, 17), (22, 6))],
    [(2025, 8, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((5, 6), (21, 21))],
    [(2025, 9, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((6, 10), (20, 4))],  # 172
    [(2025, 10, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((7, 12), (18, 42))],  # 127
    [(2025, 11, 1, 0, 0, 0, 'GMT'), ABERDEEN, ((7, 19), (16, 23))],
])
def test_known_dates_cambridge(et, coord, exp):
    result = daylength.next_suntimes(EarthDateTime(*et), *coord)
    for (t, r), e_t, e_r in zip(result, exp, ['sunrise', 'sunset']):
        assert r == e_r
        t_secs = sum([t.tm_hour*HOUR, t.tm_min*MINUTE, t.tm_sec])
        e_secs = sum([e_t[0]*HOUR, e_t[1]*MINUTE])
        print(t_secs - e_secs)
        assert abs(t_secs - e_secs) < 3 * MINUTE, f"Expected: {e_t}; Got: {t}"


