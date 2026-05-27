import math
from engg_skills_common.units import convert

def test_length_conversion():
    assert math.isclose(convert(1, 'ft', 'in')['converted_value'], 12.0)

def test_pressure_conversion():
    assert math.isclose(convert(1, 'atm', 'kpa')['converted_value'], 101.325)
