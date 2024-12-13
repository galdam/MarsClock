import math
import pytest
from marsclock.astro.ephemeris import Ephemeris

# Truth values generated at: http://www.jgiesen.de/kepler/kepler.html
anomaly_truths = [
    [0.5, 27, 48.43418, 75.83972],
    [0.5, 300, 271.36015, -118.81503],
    [0.1, 27, 29.85196, 32.84035],
    [0.1, 300, 294.79877, -70.52369],
]

@pytest.mark.parametrize('ec,M_deg,E_deg', [
    [k[0], k[1], k[2]] for k in anomaly_truths
])
def test_eccentric_anomaly_calculation(ec, M_deg, E_deg):
    M_rad = math.radians(M_deg)
    result_E_rad = Ephemeris._calc_keplers_equation(ec, M_rad)
    result_E_deg = math.degrees(result_E_rad)
    assert E_deg == pytest.approx(result_E_deg, rel=1e-6)


@pytest.mark.parametrize('ec,E_deg,phi_deg', [
    [k[0], k[2], k[3]] for k in anomaly_truths
])
def test_true_anomaly_calculation(ec, E_deg, phi_deg):
    E_rad = math.radians(E_deg)
    result_phi_rad = Ephemeris._calc_true_anomaly_rad(ec, E_rad)
    result_phi_deg = math.degrees(result_phi_rad)
    assert phi_deg == pytest.approx(result_phi_deg, rel=1e-6)



