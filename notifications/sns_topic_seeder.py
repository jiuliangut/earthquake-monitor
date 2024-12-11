"""Creates SNS topics based of region and magnitude, then seeds those topics into RDS."""

import os
import logging
import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import boto3
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection() -> connection:
    """ Establishes a connection with database. """

    logging.info("Attempting to connect to the database")
    try:
        conn = psycopg2.connect(dbname=os.getenv("DB_NAME"),
                                user=os.getenv("DB_USER"),
                                password=os.getenv("DB_PASSWORD"),
                                host=os.getenv("DB_HOST"),
                                port=os.getenv("DB_PORT"))
        logging.info("Database connection successful.")
        return conn
    except KeyError as e:
        logging.error("%s missing from environment variables.", e)
        raise
    except psycopg2.OperationalError as e:
        logging.error("Error connecting to database: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error while connecting to database: %s", e)
        raise


def get_cursor(connect: connection) -> cursor:
    """ Create a cursor to send and receive data. """
    logging.info("Creating database cursor")
    try:
        return connect.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        logging.error("Failed to create cursor: %s", e)
        raise


def get_regions(cursor: cursor) -> list[str]:
    """Gets all the region names"""

    query = "SELECT region_name from regions"

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        region_names = [row['region_name'] for row in result]
        return region_names
    except psycopg2.OperationalError as e:
        logging.error(
            "Operational error occurred connecting whilst fetching live metrics: %s", e)
        raise
    except Exception as e:
        logging.error("Error occurred whilst fetching live metrics: %s", e)
        raise


def create_sns_topic():
    """Creates SNS topics based on magnitude and regions"""

    regions = get_regions(cursor_)
    magnitudes = [0, 4, 7]

    topics = []

    regions = [region.replace("&", "").replace(
        "(", "").replace(")", "").replace(",", "").replace(" ", "_") for region in regions]

    for region in regions:
        for magnitude in magnitudes:
            topics.append(f"{region}_{magnitude}")

    print(topics)

    topic_arns = []

    for topic in topics:
        try:
            response = sns_client.create_topic(Name=topic)
            topic_arns.append((topic, response['TopicArn']))
            print(f"Created topic: {topic} (ARN: {response['TopicArn']})")
        except Exception as e:
            print(f"Error creating topic {topic}: {e}")

    seed_topics_table(topic_arns, cursor_, conn)


def seed_topics_table(topic_arns: dict, cursor: cursor, conn: connection):
    """Seeds the topics table with topic name and topic_arns"""

    query = "INSERT INTO topics (topic_name, topic_arn) VALUES (%s, %s)"

    try:
        cursor.executemany(query, topic_arns)
        conn.commit()
        logging.info("Successfully seeded topics table")
    except psycopg2.OperationalError as e:
        logging.error(
            "Operational error occurred connecting whilst fetching live metrics: %s", e)
        raise
    except Exception as e:
        logging.error("Error occurred whilst fetching live metrics: %s", e)
        raise


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    cursor_ = get_cursor(conn)

    sns_client = boto3.client('sns')
    create_sns_topic()
