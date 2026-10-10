import pytest
from app.utils.distance import calculate_haversine_distance

def test_haversine_distance_calculation():
    # Rampur PHC (28.8074, 79.0274) to Bilaspur CHC (28.8850, 79.2680)
    # Expected distance ~24-25 km
    dist = calculate_haversine_distance(28.8074, 79.0274, 28.8850, 79.2680)
    assert 20.0 <= dist <= 30.0

def test_haversine_same_point():
    dist = calculate_haversine_distance(28.8074, 79.0274, 28.8074, 79.0274)
    assert dist == 0.0
