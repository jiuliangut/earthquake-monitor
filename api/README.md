# 🌍📡 Earthquake Monitor API
API to allow technical users to query the database and extract information in real-time
## 🗂️ Endpoints
 Below are the endpoints that users can use to navigate interact with the API which queries the database.

### 1️⃣ Get Earthquake Details by ID
- 🛠️ **Endpoint**: `GET /earthquake/{id}`
- 📄 **Description**: Get information about a specific earthquake using ID
- 🔗 **Path Parameters**:
  - `id` (string, required): ID of the earthquake
- 💡 **Example**: GET `/earthquake/783`


### 2️⃣ Get Earthquakes by Magnitude
- 🛠️ **Endpoint**: `GET /earthquakes/magnitude`
- 📄 **Description**: Get list of earthquakes within a given magnitude range
- 📋 **Query Parameters**:
  - `min_magnitude` (float, optional): Minimum magnitude 
  - `max_magnitude` (float, optional): Maximum magnitude 
  - If only one is given, will give all earthquakes either above or below it
- 💡 **Example**: GET `/earthquakes/magnitude?min_magnitude=4.0&max_magnitude=7.0`


### 3️⃣ Get Earthquakes by Region
- 🛠️ **Endpoint**: `GET /earthquakes/region`
- 📄 **Description**: Get all earthquakes occurring within a specific region
- 📋 **Query Parameters**:
  - `region` (string, required): ID of the region (one of the 36 we have defined)
- 💡 **Example**: GET `/earthquakes/region?region_id=3`


### 4️⃣ Get Earthquakes by Date
- 🛠️ **Endpoint**: `GET /earthquakes/date`
- 📄 **Description**: Get earthquakes from within a specific date range
- 📋 **Query Parameters**:
  - `start_date` (string, required): Start date (DD-MM-YYYY)
  - `end_date` (string, required): End date (DD-MM-YYYY)
  - `sort` (string, optional): Sort order for results:
    - `ascending`, `descending`; default is `ascending`
- 💡 **Example**:
  GET `/earthquakes/date?start_date=01-01-2001&end_date=02-02-2002&sort=descending`

### 5️⃣ Get Earthquakes by Alert Level
- 🛠️ **Endpoint**: `GET /earthquakes/alert/colour`
- 📄 **Description**: Get earthquakes of a specific alert level
- 📋 **Query Parameters**:
  - `colour` (string, required). Filter earthquakes by alert level: 
    - `green`, `yellow`, `orange`, `red`
- 💡 **Example**:
  GET `/earthquakes/alert/colour=red`

### 6️⃣ Get a Prediction Magnitude of the Next Earthquake
- 🛠️ **Endpoint**: `GET /earthquakes/predict`
- 📄 **Description**: Make a prediction for the magnitude on an earthquake based on its location
- 📋 **Query Parameters**:
  - `lat` (string: required): Latitude coordinate
  - `long` (string: required): Longitude coordinate
- 💡 **Example**: 
  GET `/earthquakes/predict?lat=30.0&long=-120.0`
