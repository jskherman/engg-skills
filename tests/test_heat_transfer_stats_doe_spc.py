import math
from engg_skills_common.heat_transfer import lmtd
from engg_skills_common.stats import describe, linear_regression
from engg_skills_common.doe import two_level_factorial
from engg_skills_common.spc import individuals_chart

def test_lmtd_equal_delta_t():
    assert lmtd(10,10) == 10

def test_describe_and_regression():
    assert describe([1,2,3])['mean'] == 2
    reg = linear_regression([1,2,3], [2,4,6])
    assert math.isclose(reg['slope'], 2)
    assert math.isclose(reg['r_squared'], 1)

def test_two_level_factorial():
    runs=two_level_factorial(['T','P'])
    assert len(runs)==4

def test_individuals_chart():
    chart=individuals_chart([1,2,3,4])
    assert chart['count']==4
