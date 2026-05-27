import math
from engg_skills_common.dimensionless import reynolds_number, prandtl_number

def test_reynolds_number():
    assert math.isclose(reynolds_number(density=1000, velocity=2, length=0.05, viscosity=0.001), 100000.0)

def test_prandtl_number():
    assert math.isclose(prandtl_number(cp=4180, viscosity=0.001, thermal_conductivity=0.6), 6.966666666666667)
