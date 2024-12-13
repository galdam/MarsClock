import pytest
import marstime


@pytest.mark.parametrize("earth_time,expected", [
    ((15, 7, 1965, 1, 0, 57), (32539, 23, 25, 0)),
])
def test_marstime(earth_time, expected):
    mars_time = marstime.MarsTime.from_earthtime(earth_time)
    assert mars_time == expected

