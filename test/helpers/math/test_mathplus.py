import pytest
from marsclock.helpers.math import mathplus


@pytest.mark.parametrize("a,b,exp_q,exp_r", [
    [110, 100, 1, 10],
    [-110, 100, -1, -10],
])
def test_c_divmod(a, b, exp_q, exp_r):
    res_q, res_r = mathplus.c_divmod(a, b)
    assert res_q == exp_q
    assert res_r == exp_r


@pytest.mark.parametrize("a,b,exp_q,exp_r", [
    [110, 100, 1, 10],
    [-110, 100, -2, 90],
])
def test_divmod(a, b, exp_q, exp_r):
    res_q, res_r = divmod(a, b)
    assert res_q == exp_q
    assert res_r == exp_r

