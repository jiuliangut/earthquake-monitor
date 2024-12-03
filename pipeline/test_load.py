import pytest
import datetime
from unittest.mock import MagicMock, patch
from psycopg2.extensions import connection, cursor
from load import *


@pytest.fixture
def mock_connection():
    """Fixture for mocking a database connection."""
    mock_conn = MagicMock()
    return mock_conn


@pytest.fixture
def mock_cursor():
    """Fixture for mocking a database cursor."""
    mock_cur = MagicMock()
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


def test_insert_into_earthquake_empty_data(mock_connection, mock_cursor):
    """Test insert_into_earthquake with empty data"""
    insert_into_earthquake(mock_connection, mock_cursor, [])
    mock_cursor.fetchone.assert_not_called()
    mock_connection.commit.assert_not_called()


@patch('psycopg2.connect')
def test_get_connection_success(mock_connect):
    """Test get_connection with a successful connection."""
    # Mock the connection object returned by psycopg2.connect
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    # Call the function being tested
    conn = get_connection()

    # Assert the function returned the mocked connection
    assert conn == mock_conn
    # Ensure psycopg2.connect was called with correct arguments
    mock_connect.assert_called_once_with(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


@patch('psycopg2.connect')
def test_get_connection_db_error(mock_connect):
    """Test get_connection with a database error (OperationalError)."""

    mock_connect.side_effect = psycopg2.OperationalError("Connection error")

    with pytest.raises(psycopg2.OperationalError):
        get_connection()


@patch('psycopg2.connect')
def test_get_connection_missing_env(mock_connect):
    """Test get_connection with missing environment variables."""

    mock_connect.side_effect = KeyError('DB_NAME')

    with pytest.raises(KeyError):
        get_connection()


@patch('load.logging.error')
def test_get_cursor_creation_error(mock_connection):
    """Test get_cursor when cursor creation fails"""
    mock_connection.cursor.side_effect = Exception("Cursor creation failed")

    with pytest.raises(Exception):
        get_cursor(mock_connection)


@patch('load.logging.warning')
def test_insert_into_earthquake_no_valid_data(mock_warning, mock_connection, mock_cursor, valid_earthquake_list):
    """Test insert_into_earthquake when no valid records exist"""
    mock_cursor.fetchone.side_effect = [None, None]
    insert_into_earthquake(mock_connection, mock_cursor, valid_earthquake_list)
    mock_warning.assert_called_once_with("No valid records to insert.")


def test_insert_into_earthquake_db_error(mock_connection, mock_cursor, valid_earthquake_list):
    """Test insert_into_earthquake when DB insertion fails"""

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

    mock_cursor.executemany.side_effect = psycopg2.Error("DB error")

    with pytest.raises(psycopg2.Error):
        insert_into_earthquake(
            mock_connection, mock_cursor, valid_earthquake_list)


def test_get_foreign_key_psycopg2_error(mock_cursor):
    """Test get_foreign_key when a psycopg2 error occurs."""

    mock_cursor.execute.side_effect = psycopg2.Error("DB error")

    with pytest.raises(psycopg2.Error):
        get_foreign_key(mock_cursor, "mock_table", "mock_column", "mock_value")


def test_get_foreign_key_unexpected_error(mock_cursor):
    """Test get_foreign_key when an unexpected error occurs."""
    mock_cursor.execute.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        get_foreign_key(mock_cursor, "mock_table", "mock_column", "mock_value")
