'''API for the earthquake monitor.'''
from datetime import datetime
from flask import Flask, jsonify, request
from database import (get_earthquake_by_id,
                      get_earthquakes_by_magnitude,
                      get_earthquakes_by_date,
                      get_earthquakes_by_alert_level)

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
    if not max_magnitude:
        max_magnitude = 10.0

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


@app.route("/earthquakes/alert/<string:color>")
def endpoint_earthquakes_by_alert_color(color: str):
    """Returns all earthquakes with a certain alert level."""
    if not valid_color(color.lower()):
        return jsonify({"error": "Invalid alert level"}), 404

    earthquakes = get_earthquakes_by_alert_level(color.lower())

    if not earthquakes:
        return jsonify({"error": "No earthquakes found"}), 404
    return jsonify(earthquakes), 200


if __name__ == "__main__":
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.run(debug=True, host="0.0.0.0", port=5000)
