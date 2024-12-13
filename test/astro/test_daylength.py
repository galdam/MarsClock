import pytest

from marsclock.astro import daylength, astrotime

@pytest.mark.parametrize("et,latitude,longitude", [
    []
])
def test_known_dates(et, latitude, longitude):
    daylength.next_suntimes(et, latitude, longitude)