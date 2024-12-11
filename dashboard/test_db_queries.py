# pylint: skip-file

import pytest
from unittest.mock import MagicMock, patch
from psycopg2 import OperationalError
from db_queries import *
import pandas as pd


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


@patch('psycopg2.connect')
def test_get_connection_success(mock_connect):
    """Test get_connection with a successful connection."""

    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    conn = get_connection()

    assert conn == mock_conn

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


@patch('db_queries.logging.error')
def test_get_cursor_creation_error(mock_connection):
    """Test get_cursor when cursor creation fails"""
    mock_connection.cursor.side_effect = Exception("Cursor creation failed")

    with pytest.raises(Exception):
        get_cursor(mock_connection)


def test_get_data_from_range_success(mock_cursor):
    """Test get_data_from_range with a successful query."""
    mock_cursor.fetchall.return_value = [
        {
            "place": "Test Place",
            "time": "2024-12-01T12:34:56",
            "felt_report_count": 5,
            "magnitude": 4.2,
            "cdi": 2.1,
            "latitude": 12.34,
            "longitude": 56.78,
            "depth": 10.5,
            "alert_type": "Test Alert",
            "magnitude_type": "Mw",
            "network_name": "Test Network",
        }
    ]

    result = get_data_from_range("2024-12-01", "2024-12-02", mock_cursor)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert result.iloc[0]["place"] == "Test Place"
    mock_cursor.execute.assert_called_once()


def test_get_data_from_range_operational_error(mock_cursor):
    """Test get_data_from_range when an OperationalError occurs."""
    mock_cursor.execute.side_effect = OperationalError("Operational error")

    with pytest.raises(OperationalError):
        get_data_from_range("2024-12-01", "2024-12-02", mock_cursor)


def test_get_data_from_range_generic_error(mock_cursor):
    """Test get_data_from_range when a generic error occurs."""
    mock_cursor.execute.side_effect = Exception("Generic error")

    with pytest.raises(Exception):
        get_data_from_range("2024-12-01", "2024-12-02", mock_cursor)


def test_get_regions_success(mock_cursor):
    """Test get_regions with a successful query."""
    mock_cursor.fetchall.return_value = [
        {"region_name": "Region A"}, {"region_name": "Region B"}]

    result = get_regions(mock_cursor)

    assert isinstance(result, list)
    assert result == ["Region A", "Region B"]
    mock_cursor.execute.assert_called_once()


def test_get_regions_operational_error(mock_cursor):
    """Test get_regions when an OperationalError occurs."""
    mock_cursor.execute.side_effect = OperationalError("Operational error")

    with pytest.raises(OperationalError):
        get_regions(mock_cursor)


def test_get_regions_generic_error(mock_cursor):
    """Test get_regions when a generic error occurs."""
    mock_cursor.execute.side_effect = Exception("Generic error")

    with pytest.raises(Exception):
        get_regions(mock_cursor)


def test_get_topic_arns_success(mock_cursor):
    """Test get_topic_arns with a successful query."""
    mock_cursor.fetchone.side_effect = [
        {"topic_arn": "arn:aws:sns:region:123456789012:TopicA"},
        {"topic_arn": "arn:aws:sns:region:123456789012:TopicB"},
    ]

    topic_names = ["TopicA", "TopicB"]
    result = get_topic_arns(topic_names, mock_cursor)

    assert isinstance(result, list)
    assert result == [
        "arn:aws:sns:region:123456789012:TopicA",
        "arn:aws:sns:region:123456789012:TopicB",
    ]
    assert mock_cursor.execute.call_count == len(topic_names)


def test_get_topic_arns_operational_error(mock_cursor):
    """Test get_topic_arns when an OperationalError occurs."""
    mock_cursor.execute.side_effect = OperationalError("Operational error")

    with pytest.raises(OperationalError):
        get_topic_arns(["TopicA"], mock_cursor)


def test_get_topic_arns_generic_error(mock_cursor):
    """Test get_topic_arns when a generic error occurs."""
    mock_cursor.execute.side_effect = Exception("Generic error")

    with pytest.raises(Exception):
        get_topic_arns(["TopicA"], mock_cursor)
