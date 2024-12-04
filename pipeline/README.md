# 🌎 Earthquake ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for processing earthquake data from the USGS Earthquake API, transforming the data into a standardized format, and loading it into a PostgreSQL database. The pipeline also includes automated testing for key transformations and loading functionality.

---

## 🗂️ Directory Structure

```
earthquake_etl/
│
├── extract.py           # Extracts earthquake data from the API
├── transform.py         # Transforms the extracted data for further processing
├── load.py              # Loads the transformed data into the PostgreSQL database
├── etl.py               # Main script to run the ETL process
├── schema.sql           # SQL script to create and initialize the database schema
├── requirements.txt     # file containing all of the dependencies needed to run the pipeline
├── test_extract.py      # Unit tests for the `extract.py` module
├── test_transform.py    # Unit tests for the `transform.py` module
├── test_load.py         # Unit tests for the `load.py` module
└── README.md            # Documentation for the project
```

---

## 📄 Modules

### **1. `extract.py`**
- **Purpose:** Fetches earthquake data from the USGS API.
- **Key Functionality:**
  - Queries the API and retrieves earthquake data for the last minute.
  - Extracts attributes such as magnitude, location, and type.
  - Handles errors, including missing data and API connection issues.
- **API URL Used:** [USGS Earthquake Feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson)
- **Tests:** `test_extract.py`

### **2. `transform.py`**
- **Purpose:** Cleans and validates the data extracted by `extract.py`.
- **Key Functionality:**
  - Cleans and standardizes fields like `felt`, `cdi`, and `alert`.
  - Validates geographic (latitude/longitude) and magnitude ranges.
  - Drops invalid records and prepares data for database insertion.
- **Tests:** `test_transform.py`

### **3. `load.py`**
- **Purpose:** Inserts cleaned data into a PostgreSQL database.
- **Key Functionality:**
  - Connects to the database using environment variables for credentials.
  - Resolves foreign keys for related tables (e.g., alert types, magnitude types).
  - Batch-inserts earthquake records into the `earthquakes` table.
- **Tests:** `test_load.py`

### **4. `etl.py`**
- **Purpose:** Runs the entire ETL pipeline.
- **Key Functionality:**
  - Combines extraction, transformation, and loading into a single script.
  - Can be run as a standalone process or triggered by an AWS Lambda event.
  - Provides logging and error handling for end-to-end execution.

### **5. `schema.sql`**
- **Purpose:** Defines the PostgreSQL database schema.
- **Key Functionality:**
  - Creates tables for earthquakes, alerts, magnitude types, and other entities.
  - Includes constraints for data integrity (e.g., latitude/longitude ranges).

---

## 📊 Testing

### **1. `test_extract.py`**
- **Purpose:** Ensures data extraction is correct.
- **Tests Include:**
  - Validation of extracting the correct data for the correct time.
  - Correct handling of missing fields and empty requests.
  - Verification of the correct output format.
  - pytest coverage: _(Insert coverage here)_

### **2. `test_transform.py`**
- **Purpose:** Ensures data transformations are correct.
- **Tests Include:**
  - Validation of latitude, longitude, magnitude, and CDI values.
  - Correct handling of missing or invalid fields.
  - Verification of the cleaned output format.
  - pytest coverage: _(Insert coverage here)_

### **3. `test_load.py`**
- **Purpose:** Validates data insertion logic into the database.
- **Tests Include:**
  - Correct mapping of foreign keys.
  - Successful batch inserts into the `earthquakes` table.
  - Handling of invalid data during database operations.
  - pytest coverage: _(Insert coverage here)_

---

## 🛠️ How to Use

### **Setup**
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables for the database connection:
    Store the following variables in a `.env` file in the directory:
   ```bash
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=your_db_port
   ```

### **Database Setup**
Initialize the database schema:
```bash
psql -H <host> -P <port> -U <username> -d <database_name> -W -f schema.sql
```

### **Run the ETL Pipeline**
To execute the ETL pipeline:
```bash
python etl.py
```

### **Run Tests**
To run the tests:
```bash
pytest test_transform.py
pytest test_load.py
```

---

## Logging and Error Handling

- Each module uses Python's `logging` library to provide detailed logs.
- Errors are handled gracefully, ensuring the pipeline can recover from failures during extraction, transformation, or loading.