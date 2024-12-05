# Earthquake Monitor API
A RESTful API to allow technical users to query the database and extract information in real-time


## Features

- Retrieves detailed information about specific earthquakes.
- Query earthquakes based on magnitude ranges.
- Get earthquakes within specific date ranges with sorting options.
- Filter earthquakes by alert levels (e.g., green, yellow, orange, red).


## API endpoints:

### 1. Get Earthquake Details by ID
- **Endpoint**: `GET /earthquake/{id}`
- **Description**: Get information about a specific earthquake using ID
- **Path Parameters**:
  - `id` (string, required): ID of the earthquake (**begins at 1**)
- **Example**: GET `/earthquake/1`


### 2. Get Earthquakes by Magnitude
- **Endpoint**: `GET /earthquakes/magnitude`
- **Description**: Get list of earthquakes within a given magnitude range
- **Query Parameters**:
  - `min_magnitude` (float, optional): Minimum magnitude 
  - `max_magnitude` (float, optional): Maximum magnitude 
  - If only one is given, will give all earthquakes either above or below it
- **Example**: GET `/earthquakes/magnitude?min_magnitude=4.0&max_magnitude=7.0`


### 3. Get Earthquakes by Date
- **Endpoint**: `GET /earthquakes/date`
- **Description**: Get earthquakes from within a specific date range
- **Query Parameters**:
  - `start_date` (string, required): Start date (YYYY-MM-DD)
  - `end_date` (string, required): End date (YYYY-MM-DD)
  - `sort` (string, optional): Sort order for results:
    - `ascending`, `descending`; default is `ascending`
- **Example**:
  GET `/earthquakes/date?start_date=01-01-2001&end_date=02-02-2002&sort=descending`

### 4. Get Earthquakes by Alert Level
- **Endpoint**: `GET /earthquakes/color`
- **Description**: Get earthquakes fo a specific alert level
- **Query Parameters**:
  - `color` (string, required). Filter earthquakes by alert level: 
    - `green`, `yellow`, `orange`, `red`
- **Example**:
  GET `/earthquakes/alert/green`
