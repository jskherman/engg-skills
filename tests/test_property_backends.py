import math
from engg_skills_common.property_backends import costald_liquid_density, get_lpg_constants, iapws95_state, iapws_saturation, pr_translated_lpg_eos, recommend_property_method

def test_costald_lpg_density_reasonable():
    c = get_lpg_constants(['propane', 'n-butane'])
    out = costald_liquid_density(
        T=300.0,
        P=1e6,
        zs=[0.5,0.5],
        Tcs=c['Tcs'],
        Vcs=c['Vcs'],
        omegas=c['omegas'],
        MWs=c['MWs'],
    )
    assert out['density_kg_m3'] > 300
    assert out['density_kg_m3'] < 800
    assert 'COSTALD' in out['method']

def test_iapws_liquid_water_state():
    out = iapws95_state(T=300.0, P=101325.0)
    assert 990 < out['density_kg_m3'] < 1005
    assert out['enthalpy_j_kg'] > 0

def test_iapws_saturation_pressure():
    out = iapws_saturation(T=373.15)
    assert math.isclose(out['saturation_pressure_pa'], 101325, rel_tol=0.02)

def test_recommend_lpg_method():
    out = recommend_property_method(components=['propane','n-butane'], application='LPG processing', pressure_pa=1.2e6)
    assert 'COSTALD' in out['recommended_method']
    assert 'Peng-Robinson' in out['recommended_method']

def test_pr_translated_lpg_eos_reports_roots():
    c = get_lpg_constants(['propane', 'n-butane'])
    out = pr_translated_lpg_eos(
        T=300.0,
        P=1e6,
        zs=[0.5, 0.5],
        Tcs=c['Tcs'],
        Pcs=c['Pcs'],
        omegas=c['omegas'],
    )
    assert out['method'] == 'thermo.eos_mix.PRMIXTranslatedPPJP'
    assert 'Z_l' in out or 'Z_g' in out
