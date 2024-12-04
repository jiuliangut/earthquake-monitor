import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import boto3
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from typing import Any


QUERY = """ SELECT
    e.earthquake_id,
    e.time,
    e.magnitude,
    e.tsunami,
    e.felt_report_count,
    e.cdi,
    e.latitude,
    e.longitude,
    e.depth,
    e.detail_url,
    a.alert_type,
    m.magnitude_type,
    n.network_name,
    t.type_name
    FROM earthquakes AS e
    JOIN alerts AS a ON e.alert_id = a.alert_id
    JOIN networks AS n ON e.network_id = n.network_id
    JOIN magnitude AS m ON e.magnitude_id = m.magnitude_id
    JOIN type AS t ON e.type_id = t.type_id;
"""

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


def get_cursor(conn: connection) -> cursor:
    """Returns cursor for the connection"""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def extract_data() -> None:
    """Extracts data from database and writes to a CSV file"""
    conn = None
    try:
        conn = get_connection()
        cur = get_cursor(conn)
        print("Executing query...")
        cur.execute(QUERY)
        results = cur.fetchall()
        column_titles = [desc[0] for desc in cur.description]

        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(column_titles)
            writer.writerows([list(row.values()) for row in results])

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
    """Uploads CSV file to S3 bucket"""
    s3_client = get_client()
    bucket_name = os.getenv("BUCKET_NAME")
    s3_key = os.path.basename(CSV_FILE)

    try:
        print(f"Uploading {CSV_FILE} to bucket...")
        s3_client.upload_file(CSV_FILE, bucket_name, s3_key)
        print("Upload successful.")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        raise


# def lambda_handler(event, context):
#     """For AWS lambda function"""
#     try:
#         extract_data()
#         upload_to_s3()
#         return {"statusCode": 200, "body": "Data upload pipeline executed successfully"}
#     except Exception as e:
#         print(f"Pipeline error: {e}")
#         return {"statusCode": 500, "body": f"Error occurred: {e}"}


if __name__ == "__main__":
    try:
        load_dotenv()
        extract_data()
        s3 = get_client()
        s3.upload_file(CSV_FILE, os.getenv("BUCKET_NAME"), CSV_FILE)
    except Exception as e:
        print(f"Execution error: {e}")
