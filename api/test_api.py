# pylint: skip-file
import requests
from unittest.mock import patch
import pytest
from api import app


@pytest.fixture
def client():
    '''API client for testing'''
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_endpoint_index(client):
    '''Test the index endpoint'''
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {
        "message": "Welcome to the Earthquake Monitor API homepage"}


@patch("api.get_earthquake_by_id")
def test_get_earthquake_by_id_endpoint(mock_db_query, client):
    '''Test the endpoint for getting earthquakes by id'''
    mock_db_query.return_value = {"id": 1, "test": "test"}
    response = client.get("/earthquakes/1")
    assert response.status_code == 200
    assert response.json == {"id": 1, "test": "test"}


@patch("api.get_earthquake_by_id")
def test_invalid_earthquake_id(mock_db_query, client):
    '''Test correct error handling when there is an invalid ID'''
    mock_db_query.return_value = None
    response = client.get("/earthquakes/200000")
    assert response.status_code == 404
    assert response.json == {"error": "Earthquake not found"}


@patch("api.get_earthquakes_by_magnitude")
def test_magnitude_endpoint(mock_db_query, client):
    '''Test the magnitude endpoint'''
    mock_db_query.return_value = [{"test": "1"}, {"test": "2"}]
    response = client.get(
        "/earthquakes/magnitude?min_magnitude=1.0&max_magnitude=8.0")
    assert response.status_code == 200
    assert response.json == [{"test": "1"}, {"test": "2"}]


@patch("api.get_earthquakes_by_magnitude")
def test_magnitude_endpoint_no_minmax(mock_db_query, client):
    '''Test correct handling of endpoint calls without query parameters'''
    mock_db_query.return_value = [{"test": "1"}, {"test": "2"}, {"test": "3"}]
    response = client.get("/earthquakes/magnitude")
    assert response.status_code == 200
    assert response.json == [{"test": "1"}, {"test": "2"}, {"test": "3"}]


@patch("api.get_earthquakes_by_magnitude")
def test_magnitude_endpoint_no_earthquakes(mock_db_query, client):
    '''Test the error handling for when no earthquakes are found'''
    mock_db_query.return_value = None
    response = client.get("/earthquakes/magnitude")
    assert response.status_code == 404
    assert response.json == {"error": "No earthquakes found"}


@patch("api.get_earthquakes_by_date")
def test_date_endpoint(mock_db_query, client):
    '''Test the data endpoint'''
    mock_db_query.return_value = {"test": "test"}
    response = client.get(
        "/earthquakes/date?start_date=2024-10-01&end_date=2024-10-10")
    assert response.status_code == 200
    assert response.json == {"test": "test"}


def test_date_endpoint_invalid_startdate(client):
    '''Test the error handling for invalid start_date format'''
    response = client.get(
        "/earthquakes/date?start_date=2024/10/01&end_date=2024-10-10")
    assert response.status_code == 400
    assert response.json == {
        "error": "Invalid start_date format. Please use YYYY-MM-DD"}


def test_date_endpoint_no_startdate(client):
    '''Test the error handling when start_date is missing'''
    response = client.get(
        "/earthquakes/date?end_date=2024-10-10")
    assert response.status_code == 404
    assert response.json == {"error": "start_date must be given"}


def test_date_endpoint_invalid_enddate(client):
    '''Test the error handling when end_date has an invalid format'''
    response = client.get(
        "/earthquakes/date?start_date=2024-10-01&end_date=2024/10/10")
    assert response.status_code == 400
    assert response.json == {
        "error": "Invalid end_date format. Please use YYYY-MM-DD"}


def test_date_endpoint_no_enddate(client):
    '''Test the error handling when end_date is missing'''
    response = client.get(
        "/earthquakes/date?start_date=2024-10-01")
    assert response.status_code == 404
    assert response.json == {"error": "end_date must be given"}


@patch("api.get_earthquakes_by_date")
def test_date_endpoint_no_earthquakes(mock_db_query, client):
    '''Test error handling when no earthquakes are found'''
    mock_db_query.return_value = None
    response = client.get(
        "/earthquakes/date?start_date=2024-10-01&end_date=2024-10-10")
    assert response.status_code == 404
    assert response.json == {"error": "No earthquakes found"}


@patch("api.get_earthquakes_by_alert_level")
def test_alert_endpoint(mock_db_query, client):
    '''Test alert endpoint'''
    mock_db_query.return_value = {"test": "test"}
    response = client.get("/earthquakes/alert/green")
    assert response.status_code == 200
    assert response.json == {"test": "test"}


def test_alert_endpoint_invalid_alert(client):
    '''Test the error handling of invalid alert levels'''
    response = client.get("/earthquakes/alert/pink")
    assert response.status_code == 404
    assert response.json == {"error": "Invalid alert level"}


@patch("api.get_earthquakes_by_alert_level")
def test_alert_endpoint_no_earthquakes(mock_db_query, client):
    '''Test the error handling for no earthquakes found'''
    mock_db_query.return_value = None
    response = client.get("/earthquakes/alert/red")
    assert response.status_code == 404
    assert response.json == {"error": "No earthquakes found"}
