'''API for the earthquake monitor.'''
from datetime import datetime
from flask import Flask, jsonify, request
from database import (get_earthquake_by_id,
                      get_earthquakes_by_magnitude,
                      get_earthquakes_by_date,
                      get_earthquakes_by_alert_level)
from model import make_prediction

app = Flask(__name__)


def valid_color(color: str) -> bool:
    """Checks whether the color is valid."""
    return color in ('green', 'yellow', 'orange', 'red')


@app.route("/", methods=["GET"])
def endpoint_index():
    """Return the enpoint for the API home page."""
    return {"message": "Welcome to the Earthquake Monitor API homepage"}


@app.route("/earthquakes/<int:earthquake_id>", methods=["GET"])
def endpoint_get_earthquake(earthquake_id: int):
    """Returns a specific earthquake"""
    earthquake = get_earthquake_by_id(earthquake_id)

    if not earthquake:
        return jsonify({"error": "Earthquake not found"}), 404

    return jsonify(earthquake), 200


@app.route("/earthquakes/magnitude", methods=["GET"])
def endpoint_get_magnitude():
    """Returns all earthquakes within a magnitude range."""
    min_magnitude = request.args.get("min_magnitude")
    max_magnitude = request.args.get("max_magnitude")

    if not min_magnitude:
        min_magnitude = -1.0
    else:
        min_magnitude = float(min_magnitude)
    if not max_magnitude:
        max_magnitude = 10.0
    else:
        max_magnitude = float(max_magnitude)

    if min_magnitude >= max_magnitude:
        return jsonify({"error": "min_magnitude must be less than max_magnitude"}), 400

    earthquakes = get_earthquakes_by_magnitude(min_magnitude, max_magnitude)

    if not earthquakes:
        return jsonify({"error": "No earthquakes found"}), 404

    return jsonify(earthquakes), 200


@app.route("/earthquakes/date", methods=["GET"])
def endpoint_get_earthquakes_between_date():
    """Returns all earthquakes between two dates."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort = request.args.get("sort")

    if not start_date:
        return jsonify({"error": "start_date must be given"}), 404

    try:
        start_date = datetime.strptime(
            start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start_date format. Please use YYYY-MM-DD"}), 400

    if not end_date:
        return jsonify({"error": "end_date must be given"}), 404

    try:
        end_date = datetime.strptime(
            end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid end_date format. Please use YYYY-MM-DD"}), 400

    if sort:
        sort = "DESC"
    else:
        sort = "ASC"

    earthquakes = get_earthquakes_by_date(start_date, end_date, sort)

    if not earthquakes:
        return jsonify({"error": "No earthquakes found"}), 404
    return jsonify(earthquakes), 200


@app.route("/earthquakes/alert/<string:colour>")
def endpoint_earthquakes_by_alert_colour(colour: str):
    """Returns all earthquakes with a certain alert level."""
    if not valid_color(colour.lower()):
        return jsonify({"error": "Invalid alert level"}), 404

    earthquakes = get_earthquakes_by_alert_level(colour.lower())

    if not earthquakes:
        return jsonify({"error": "No earthquakes found"}), 404
    return jsonify(earthquakes), 200


def check_length_of_coordinates(coordiante: float):
    """Ensures that the coordinates are 6 decimal points"""
    if '.' in str(coordiante) and len(str(coordiante).split('.')[1]) > 6:
        return round(coordiante, 6)
    return coordiante


@app.route("/earthquakes/predict")
def endpoint_earthquake_prediction():
    """Returns the predicted magnitude of an earthquake with given coordinates"""
    latitude = request.args.get("lat")
    longitude = request.args.get("long")

    if not latitude or not longitude:
        return jsonify({"error": "both lat and long must be given"}), 400

    if not isinstance(latitude, float):
        try:
            latitude = float(latitude)
        except:
            return jsonify({"error": "lat must be in float format"}), 400

    if not -90.0 <= latitude <= 90.0:
        return jsonify({"error": "lat must be between -90.0 and 90.0"}), 400

    if not isinstance(longitude, float):
        try:
            longitude = float(longitude)
        except:
            return jsonify({"error": "long must be in float format"}), 400

    if not -180.0 <= longitude <= 180.0:
        return jsonify({"error": "long must be between -90.0 and 90.0"}), 400

    latitude = check_length_of_coordinates(latitude)
    longitude = check_length_of_coordinates(longitude)

    prediction = make_prediction(latitude, longitude).tolist()

    if not prediction:
        return jsonify({"error": "Unexpected server error"}), 500

    return prediction


if __name__ == "__main__":
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(debug=True, host="0.0.0.0", port=5000)
