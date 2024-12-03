import pytest
import datetime
from unittest.mock import MagicMock, patch
from psycopg2.extensions import connection, cursor
from load import *


@pytest.fixture
def mock_connection():
    """Fixture for mocking a database connection."""
    mock_conn = MagicMock(spec=connection)
    return mock_conn


@pytest.fixture
def mock_cursor():
    """Fixture for mocking a database cursor."""
    mock_cur = MagicMock(spec=cursor)
    return mock_cur


@pytest.fixture
def valid_earthquake_list():
    return [{
        'at': datetime.datetime(2024, 12, 3, 13, 42, 51),
        'event_url': 'https:example.com',
        'felt': 0,
        'location': '8 km SW of Volcano, Hawaii',
        'tsunami': 0,
        'magnitude': 1.79,
        'network': 'hv',
        'alert': 'green',
        'magnitude_type': 'md',
        'type': 'earthquake',
        'cdi': 2,
        'longitude': -155.28,
        'latitude': 19.38
    },
        {
        'at': datetime.datetime(2024, 12, 1, 3, 22, 15),
        'event_url': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/us202433689.geojson',
        'felt': 4.0,
        'location': '10 km NE of Ridgecrest, California',
        'magnitude': 4.25,
        'network': 'ci',
        'alert': 'yellow',
        'magnitude_type': 'ml',
        'type': 'quarry',
        'tsunami': 0,
        'cdi': 3.2,
        'longitude': -117.5245,
        'latitude': 35.7038
    }]


@pytest.fixture
def valid_query():
    return """INSERT INTO earthquakes (time, tsunami, felt_report_count, magnitude, 
            cdi, latitude, longitude, detail_url, alert_id, magnitude_id, network_id, type_id) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


def test_get_foreign_key_valid(mock_cursor):
    """Test get_foreign_key with valid data."""
    mock_cursor.fetchone.return_value = {'id': 1}
    result = get_foreign_key(mock_cursor, "alerts", "alert_type", "green")
    assert result == 1
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM alerts WHERE alert_type = 'green'"
    )


def test_get_foreign_key_invalid(mock_cursor):
    """Test get_foreign_key with invalid data."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError):
        get_foreign_key(mock_cursor, "alerts", "alert_type", "invalid")
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM alerts WHERE alert_type = 'invalid'"
    )


def test_insert_into_earthquake_valid(mock_connection, mock_cursor, valid_earthquake_list):
    """Test insert_into_earthquake with valid data"""
    mock_cursor.fetchone.side_effect = [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4},
        {"id": 5},
        {"id": 6},
        {"id": 7},
        {"id": 8}
    ]

    insert_into_earthquake(mock_connection, mock_cursor, valid_earthquake_list)

    assert mock_cursor.fetchone.call_count == 8

    mock_connection.commit.assert_called_once()
