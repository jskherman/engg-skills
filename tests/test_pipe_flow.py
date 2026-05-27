from engg_skills_common.fluids import darcy_friction_factor, pipe_pressure_drop

def test_laminar_friction_factor():
    f, method, warnings = darcy_friction_factor(1000)
    assert f == 0.064
    assert method in {'laminar-64/Re', 'fluids.friction_factor(Clamond)'}
    assert warnings == []

def test_pipe_pressure_drop_positive():
    out = pipe_pressure_drop(length=100, diameter=0.05, flow_m3_s=0.001, density=998, viscosity=0.001)
    assert out['total_pressure_drop_pa'] > 0
    assert out['reynolds'] > 0
