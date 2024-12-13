import pytest
from drivers.display import palette


def test_expected_values_for_palette_mono():
    p = palette.PaletteMono()
    assert p.nbits == 1
    assert p.ncolors == 2

    assert p.BLACK == 0
    assert p.DARK_GRAY == 0
    assert p.LIGHT_GRAY == 0
    assert p.WHITE == 1
    assert p.RED == 0


def test_expected_values_for_palette_greyscale():
    p = palette.PaletteGreyscale()
    assert p.nbits == 2
    assert p.ncolors == 4

    assert p.BLACK == 0
    assert p.DARK_GRAY == 1
    assert p.LIGHT_GRAY == 2
    assert p.WHITE == 3
    assert p.RED == 1


def test_expected_values_for_palette_tricolor():
    p = palette.PaletteTricolor()
    assert p.nbits == 2
    assert p.ncolors == 3

    assert p.BLACK == 0
    assert p.DARK_GRAY == 1
    assert p.LIGHT_GRAY == 1
    assert p.WHITE == 2
    assert p.RED == 1

