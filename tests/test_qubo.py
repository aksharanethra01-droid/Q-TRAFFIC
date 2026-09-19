import numpy as np
from quantum.qubo_builder import build_qubo, variable_names
from quantum.decoder import decode_bitstring

def context():
    return {f"J{i}":{"vehicles":20+i*5,"queue":8+i*2,"capacity":50,"waiting":10,"throughput":20,
                       "congestion":.4,"shock":0,"emergency_delay":0} for i in range(1,5)}

def test_exactly_12_variables():
    assert len(variable_names()) == 12

def test_exactly_one_constraint():
    m=build_qubo(context())
    valid="100010001001"
    invalid="110010001000"
    assert decode_bitstring(valid)[1]
    assert not decode_bitstring(invalid)[1]
    assert m.matrix.shape == (12,12)

def test_qubo_finite():
    m=build_qubo(context())
    assert np.isfinite(m.matrix).all()
    assert np.isfinite(m.linear).all()
