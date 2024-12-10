# pylint: skip-file

from datetime import datetime, timedelta
import pandas as pd
from dashboard import *


def test_validate_df():
    """Test the validate_df function."""
    input_data = pd.DataFrame({
        "latitude": ["34.5", "45.6"],
        "longitude": ["-120.2", "-78.3"],
        "magnitude": ["4.5", "5.6"],
        "depth": ["10.0", "12.0"],
        "cdi": ["2.5", "3.0"]
    })

    expected_data = pd.DataFrame({
        "latitude": [34.5, 45.6],
        "longitude": [-120.2, -78.3],
        "magnitude": [4.5, 5.6],
        "depth": [10.0, 12.0],
        "cdi": [2.5, 3.0]
    })

    output_data = validate_df(input_data)
    pd.testing.assert_frame_equal(output_data, expected_data)


def test_prepare_map_data():
    """Test the prepare_map_data function."""
    input_data = pd.DataFrame({
        "time": [datetime(2024, 12, 1, 15, 0), datetime(2024, 12, 2, 10, 0)],
        "magnitude": [5.0, 6.0],
        "alert_type": ["green", "red"],
    })

    expected_data = pd.DataFrame({
        "time": ["2024-12-01 15:00:00", "2024-12-02 10:00:00"],
        "magnitude": [5.0, 6.0],
        "alert_type": ["green", "red"],
        "size": [7500.0, 9000.0],
        "colour": [[0, 255, 0], [255, 0, 0]]
    })

    output_data = prepare_map_data(input_data)
    pd.testing.assert_frame_equal(output_data, expected_data)


def test_get_color_map():
    """Test the get_color_map function."""
    color_map = get_color_map()
    assert color_map == {
        "green": [0, 255, 0],
        "yellow": [255, 255, 0],
        "orange": [255, 140, 0],
        "red": [255, 0, 0],
    }


def test_get_last_weeks_monday():
    """Test the get_last_weeks_monday function."""
    today = datetime(2024, 12, 9)
    expected_monday = (
        today - timedelta(weeks=1, days=today.weekday())).strftime("%Y-%m-%d")
    output_monday = get_last_weeks_monday()
    assert output_monday == expected_monday
