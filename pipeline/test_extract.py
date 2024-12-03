# pylint: skip-file

from unittest.mock import patch
from datetime import datetime, timedelta
from extract import get_data


@patch('extract.requests.get')
def test_get_data_valid_response(mock_get):
    mock_response = {
        "features": [
            {
                "properties": {
                    "updated": (datetime.now() - timedelta(seconds=30)).timestamp() * 1000,
                    "time": (datetime.now() - timedelta(seconds=40)).timestamp() * 1000,
                    "detail": "http://example.com/quake1",
                    "felt": 5,
                    "place": "Location A",
                    "tsunami": 0,
                    "mag": 4.5,
                    "net": "us",
                    "alert": None,
                    "magType": "mb",
                    "type": "earthquake",
                    "cdi": 3.0,
                },
                "geometry": {
                    "coordinates": [120.123, -35.678]
                }
            }
        ]
    }
    mock_get.return_value.json.return_value = mock_response

    result = get_data()

    assert len(result) == 1
    assert result[0]["event_url"] == "http://example.com/quake1"
    assert result[0]["location"] == "Location A"
    assert result[0]["magnitude"] == 4.5
    assert result[0]["latitude"] == -35.678
    assert result[0]["longitude"] == 120.123


@patch('extract.requests.get')
def test_get_data_no_recent_data(mock_get):
    mock_response = {
        "features": [
            {
                "properties": {
                    "updated": (datetime.now() - timedelta(minutes=10)).timestamp() * 1000,
                    "time": (datetime.now() - timedelta(minutes=10)).timestamp() * 1000,
                    "detail": "http://example.com/quake2",
                    "felt": None,
                    "place": "Location B",
                    "tsunami": 1,
                    "mag": 3.0,
                    "net": "ci",
                    "alert": "green",
                    "magType": "ml",
                    "type": "earthquake",
                    "cdi": None,
                },
                "geometry": {
                    "coordinates": [130.456, -25.678]
                }
            }
        ]
    }
    mock_get.return_value.json.return_value = mock_response

    result = get_data()

    assert len(result) == 0


@patch('extract.requests.get')
def test_get_data_missing_fields(mock_get):
    mock_response = {
        "features": [
            {
                "properties": {
                    "updated": (datetime.now() - timedelta(seconds=30)).timestamp() * 1000,
                    "time": (datetime.now() - timedelta(seconds=30)).timestamp() * 1000,
                    "place": "Location C",
                    "mag": 2.5,
                },
                "geometry": {
                    "coordinates": [110.456, -15.678]
                }
            }
        ]
    }
    mock_get.return_value.json.return_value = mock_response

    result = get_data()

    assert len(result) == 1
    assert result[0]["location"] == "Location C"
    assert result[0]["magnitude"] == 2.5
    assert result[0]["felt"] is None
    assert result[0]["alert"] is None
    assert result[0]["latitude"] == -15.678


@patch('extract.requests.get')
def test_get_data_empty_response(mock_get):
    mock_response = {"features": []}
    mock_get.return_value.json.return_value = mock_response

    result = get_data()

    assert len(result) == 0
