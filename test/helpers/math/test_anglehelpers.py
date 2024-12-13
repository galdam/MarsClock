
import pytest
from marsclock.helpers.math import anglehelpers


@pytest.mark.parametrize("angle,expected", [
    [0, 0], [180, 180], [359, 359],
    [360, 0], [370, 10], [730, 10],
    [-10, 350], [-180, 180], [-360, 0],
])
def test_modulo_degrees_360(angle, expected):
    result = anglehelpers.modulo_degrees_360(angle)
    assert result == expected


@pytest.mark.parametrize("angle,expected", [
    [0, 0], [-90, -90], [90, 90],
    [-179, -179], [179, 179],
    [-190, 170], [190, -170],
])
def test_modulo_degrees_180(angle, expected):
    result = anglehelpers.modulo_degrees_180(angle)
    assert result == expected



