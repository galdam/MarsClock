import pytest
from marsclock.astro.astrotime import EarthDateTime, is_bst


@pytest.mark.parametrize("year", [
    1900, 1999, 2001, 2002, 2003, 2005, 2006, 2007, 2009, 2010, 2011, 2013,
    2100, 2200, 2300, 2500, 2600, 2700, 2900])
def test_non_leap_years(year):
    assert not EarthDateTime._is_leap_year(year)


@pytest.mark.parametrize("year", [
    1984, 2000, 2004, 2008, 2012, 2016, 2020, 2024,
    2028, 2032, 2036, 2040, 2044, 2048, 2052, 2068])
def test_leap_years(year):
    assert EarthDateTime._is_leap_year(year)


@pytest.mark.parametrize("year,month,mday,expected", [
    [2024, 1, 1, 0], [2024, 1, 31, 2],
    [2024, 2, 1, 3], [2024, 2, 29, 3],
    [2024, 3, 1, 4], [2024, 3, 31, 6],
    [2024, 4, 1, 0], [2024, 4, 30, 1],
])
def test_week_day(year, month, mday, expected):
    result = EarthDateTime._calc_weekday(year, month, mday)
    assert result == expected


def test_number_of_months_in_year():
    assert EarthDateTime._months_in_year() == len(EarthDateTime._days_in_months())


@pytest.mark.parametrize("year,month,weekday,expected", [
    [2024, 1, 3, 25], [2024, 1, 4, 26], [2024, 1, 5, 27],
    [2024, 1, 6, 28], [2024, 1, 0, 29], [2024, 1, 1, 30],
    [2024, 1, 2, 31], [2024, 3, 0, 25], [2024, 3, 1, 26],
    [2024, 3, 2, 27], [2024, 3, 3, 28], [2024, 3, 4, 29],
    [2024, 3, 5, 30], [2024, 3, 6, 31],
])
def test_last_day_of_week(year, month, weekday, expected):
    result = EarthDateTime.last_weekday_of_month(year, month, weekday)
    assert result == expected


@pytest.mark.parametrize("time_tup,expected", [
    [(2024, 3, 31, 0, 59, 0), False], [(2024, 3, 31, 1, 0, 0), True],
    [(2024, 10, 27, 0, 59, 0), True], [(2024, 10, 27, 1, 0, 0), False],
    [(2025, 3, 30, 0, 59, 0), False], [(2025, 3, 30, 1, 0, 0), True],
    [(2025, 10, 26, 0, 59, 0), True], [(2025, 10, 26, 1, 0, 0), False],
    [(2026, 3, 29, 0, 59, 0), False], [(2026, 3, 29, 1, 0, 0), True],
    [(2026, 10, 25, 0, 59, 0), True], [(2026, 10, 25, 1, 0, 0), False],
])
def test_is_bst(time_tup, expected):
    assert is_bst(EarthDateTime(*time_tup, tm_dst=0)) == expected


@pytest.mark.parametrize("time_tup,expected", [
    [(2024, 3, 31, 1, 59, 0), False], [(2024, 3, 31, 2, 0, 0), True],
    [(2024, 10, 27, 1, 59, 0), True], [(2024, 10, 27, 2, 0, 0), False],
    [(2025, 3, 30, 1, 59, 0), False], [(2025, 3, 30, 2, 0, 0), True],
    [(2025, 10, 26, 1, 59, 0), True], [(2025, 10, 26, 2, 0, 0), False],
    [(2026, 3, 29, 1, 59, 0), False], [(2026, 3, 29, 2, 0, 0), True],
    [(2026, 10, 25, 1, 59, 0), True], [(2026, 10, 25, 2, 0, 0), False],
])
def test_is_bst_cet(time_tup, expected):
    assert is_bst(EarthDateTime(*time_tup, tm_tzone='CET', tm_dst=0)) == expected
