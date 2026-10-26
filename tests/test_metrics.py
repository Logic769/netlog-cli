import pytest
from netlog.core.metrics import generate_sparkline, RateCalculator

def test_sparkline_generation():
    assert generate_sparkline([]) == ""
    assert generate_sparkline([0.0, 0.0]) == "  "
    
    values = [0.0, 50.0, 100.0]
    spark = generate_sparkline(values)
    assert len(spark) == 3
    assert spark[-1] == "█"
    assert spark[0] == " "

def test_rate_calculator_sparkline_integration():
    calc = RateCalculator()
    snap = calc.capture_snapshot()
    assert hasattr(snap, "download_sparkline")
    assert hasattr(snap, "upload_sparkline")
