from ai.predictor import TrafficPredictor, HORIZONS, LEVELS

def test_forecasts_generated():
    p=TrafficPredictor()
    p.observe("J1",20,8,10,50)
    p.observe("J1",25,10,12,50)
    out=p.predict("J1")
    assert [x.horizon_seconds for x in out]==HORIZONS
    assert all(x.congestion_level in LEVELS for x in out)
