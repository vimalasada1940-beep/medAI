import pytest
from app.services.burn_rate import calculate_burn_rate_from_list

def test_burn_rate_normal():
    # 7 days of consumption: sum = 350 -> avg = 50.0
    quantities = [50, 45, 55, 50, 48, 52, 50]
    burn = calculate_burn_rate_from_list(quantities, days=7)
    assert burn == 50.0

def test_burn_rate_empty_and_zero():
    assert calculate_burn_rate_from_list([], days=7) == 0.0
    assert calculate_burn_rate_from_list([0, 0, 0, 0, 0, 0, 0], days=7) == 0.0
    assert calculate_burn_rate_from_list([10], days=0) == 0.0

def test_burn_rate_rounding():
    # sum = 100 over 7 days -> 14.2857 -> 14.29
    quantities = [14, 15, 14, 14, 15, 14, 14]
    burn = calculate_burn_rate_from_list(quantities, days=7)
    assert burn == 14.29
