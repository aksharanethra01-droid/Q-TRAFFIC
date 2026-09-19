from prediction.predictor import predict_junction_traffic


def test_prediction_has_three_horizons():
    result = predict_junction_traffic(30, 10, 25, 60)
    assert set(result.keys()) == {"1min", "3min", "5min"}
    assert all(value >= 0 for value in result.values())
