# pylint: skip-file

from transform import *
import pytest
import datetime


@pytest.fixture
def valid_earthquake_dict():
    """Fixture for valid dict"""
    return [{
        'at': datetime.datetime(2024, 12, 3, 13, 42, 51, 530000),
        'event_url': 'https:example.com',
        'felt': None,
        'location': '8 km SW of Volcano, Hawaii',
        'tsunami': 0,
        'magnitude': 1.79,
        'network': 'hv',
        'alert': None,
        'magnitude_type': 'md',
        'type': 'earthquake',
        'cdi': None,
        'longitude': -155.28,
        'latitude': 19.38,
        'depth': 13.05
    }]


@pytest.fixture
def invalid_earthquake_dict():
    """Fixture for invalid dict"""
    return [{
        'at': datetime.datetime(2024, 12, 3, 13, 42, 51, 530000),
        'event_url': 'https:example.com',
        'felt': 0,
        'location': '8 km SW of Volcano, Hawaii',
        'tsunami': 0,
        'magnitude': None,
        'network': 'hv',
        'alert': 'green',
        'magnitude_type': 'md',
        'type': 'earthquake',
        'cdi': 111,
        'longitude': -155.28,
        'latitude': 119.38,
        'depth': 99999
    }]


def test_is_valid_latitude():
    """Tests for is_valid_latitude"""
    assert is_valid_latitude(0) == True
    assert is_valid_latitude(-18.76) == True
    assert is_valid_latitude(999) == False
    assert is_valid_latitude("Inavlid") == False


def test_is_valid_longitude():
    """Tests for is_valid_longitude"""
    assert is_valid_longitude(180) == True
    assert is_valid_longitude(-175.76) == True
    assert is_valid_longitude(999) == False
    assert is_valid_longitude("Inavlid") == False


def test_is_valid_magnitude():
    """Tests for is_valid_magnitude"""
    assert is_valid_magnitude(-5.34) == True
    assert is_valid_magnitude(12) == True
    assert is_valid_magnitude(20) == False
    assert is_valid_magnitude("Inavlid") == False


def test_is_valid_cdi():
    """Tests for is_valid_cdi"""
    assert is_valid_cdi(3) == True
    assert is_valid_cdi(6.78) == True
    assert is_valid_cdi(-1) == False
    assert is_valid_cdi("Inavlid") == False


def test_is_valid_depth():
    """Tests for is_valid_depth"""
    assert is_valid_depth(3) == True
    assert is_valid_depth(69.78) == True
    assert is_valid_depth(-1111) == False
    assert is_valid_depth("Inavlid") == False


def test_clean_data_valid(valid_earthquake_dict):
    """Tests for clean_data"""
    result = clean_data(valid_earthquake_dict)

    assert result[0]["at"] == datetime.datetime(2024, 12, 3, 13, 42, 51)
    assert result[0]["felt"] == 0
    assert result[0]["magnitude"] == 1.79
    assert result[0]["alert"] == 'green'
    assert result[0]['cdi'] == 0.0


def test_clean_data_invalid(invalid_earthquake_dict):
    """Test clean_data when it has an invalid dict"""
    result = clean_data(invalid_earthquake_dict)

    assert len(result) == 0
    assert result == []


def test_clean_data_empty_input():
    """Test clean_data when given an empty list"""
    with pytest.raises(ValueError):
        clean_data([])


def test_clean_data_invalid_input():
    """Test clean_data when given invalid input"""
    with pytest.raises(ValueError):
        clean_data("Not a list")
