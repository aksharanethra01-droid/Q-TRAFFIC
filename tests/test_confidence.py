from prediction.confidence import calculate_confidence

def test_confidence_is_percentage():
    value = calculate_confidence(10, 60, 30, 35, 30)
    assert 0 <= value <= 100
