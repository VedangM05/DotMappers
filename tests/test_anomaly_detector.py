import pytest
from src.anomaly_detector import anomaly_detector

def test_anomaly_detection_execution():
    """Verify anomaly detection engine runs and returns structured anomalies."""
    res = anomaly_detector.detect_anomalies()
    assert "total_anomalies" in res
    assert "critical_count" in res
    assert "warning_count" in res
    assert "narrative_summary" in res
    assert res["total_anomalies"] > 0
    assert len(res["anomalies"]) == res["total_anomalies"]
