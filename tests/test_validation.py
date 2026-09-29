import pandas as pd

def test_confidence_range():
    df = pd.DataFrame({"confidence": [0.0, 0.5, 1.0]})
    assert df["confidence"].between(0, 1).all()

def test_record_ids_unique():
    df = pd.DataFrame({"record_id": ["CS-0001", "CS-0002"]})
    assert df["record_id"].is_unique
