"""Script to extract earthquake data from RDS and upload to S3 bucket as CSV"""
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import boto3
import psycopg2
import psycopg2.extras
import pandas as pd
from psycopg2.extensions import connection, cursor

QUERY = """ 
SELECT *
FROM earthquakes AS e
JOIN alerts AS a ON e.alert_id = a.alert_id
JOIN networks AS n ON e.network_id = n.network_id
JOIN magnitude AS m ON e.magnitude_id = m.magnitude_id
JOIN type AS t ON e.type_id = t.type_id;
"""

COLUMNS = [
    'earthquake_id', 'time', 'magnitude', 'tsunami', 'felt_report_count', 'cdi',
    'latitude', 'longitude', 'depth', 'detail_url', 'alert_type', 'magnitude_type',
    'network_name', 'type_name']


CSV_FILE = f"/tmp/{datetime.today().strftime('%Y-%m-%d')}_data.csv"


def get_connection() -> connection:
    """Gets connection to database"""
    return psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )


def extract_data() -> None:
    """Extracts data from database and writes to a CSV file"""
    conn = None
    try:
        conn = get_connection()
        print("Executing query...")
        earthquakes = pd.read_sql(QUERY, conn)
        earthquakes = earthquakes[COLUMNS]
        earthquakes.to_csv(CSV_FILE, index=False, encoding="utf-8")
        print(f"Data successfully written to {CSV_FILE}")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_client():
    """Returns S3 client using env credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY")
    )


def upload_to_s3():
    """Uploads CSV file to S3 bucket and clears temp file"""
    s3_client = get_client()
    bucket_name = os.getenv("BUCKET_NAME")
    s3_key = os.path.basename(CSV_FILE)
    try:
        print(f"Uploading {CSV_FILE} to bucket...")
        s3_client.upload_file(CSV_FILE, bucket_name, s3_key)
        os.remove(CSV_FILE)
        print("Upload successful.")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        raise


def lambda_handler(event, context):
    """For AWS lambda function"""
    try:
        load_dotenv()
        extract_data()
        s3 = get_client()
        s3.upload_file(CSV_FILE, os.getenv("BUCKET_NAME"), CSV_FILE)
        return {"statusCode": 200, "body": "Data upload pipeline executed successfully"}
    except Exception as e:
        print(f"Execution error: {e}")
        return {"statusCode": 500, "body": f"Error occurred: {e}"}


if __name__ == "__main__":
    try:
        load_dotenv()
        extract_data()
        s3 = get_client()
        s3.upload_file(CSV_FILE, os.getenv("BUCKET_NAME"), CSV_FILE)
    except Exception as e:
        print(f"Execution error: {e}")
