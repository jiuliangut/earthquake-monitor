'''Module that handles the data checking and sends notifications to the correct subscriptions'''
import os
import logging
from dotenv import load_dotenv
import re
import boto3
from boto3 import client
from psycopg2 import connect, OperationalError
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_connection() -> connection:
    '''Function to get the connection to the RDS'''
    logging.info("Attempting to connect to the database")
    try:
        conn = connect(dbname=os.getenv("DB_NAME"),
                       user=os.getenv("DB_USER"),
                       password=os.getenv("DB_PASSWORD"),
                       host=os.getenv("DB_HOST"),
                       port=os.getenv("DB_PORT"))
        logging.info("Database connection successful.")
        return conn
    except KeyError as e:
        logging.error("%s missing from environment variables.", e)
        raise
    except OperationalError as e:
        logging.error("Error connecting to database: %s", e)
        raise
    except Exception as e:
        logging.error("Unexpected error while connecting to database: %s", e)
        raise


def get_cursor(conn: connection) -> cursor:
    '''Function to get the cursor for the RDS connection'''
    logging.info("Creating database cursor")
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        logging.error("Failed to create cursor: %s", e)
        raise


def get_client() -> client:
    '''Function to get a client for the SNS service'''
    return boto3.client('sns',
                        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"))


def get_earthquake_regions(earthquake_data: dict, curs: cursor) -> list[str]:
    '''Function to find the regions that the earthquake was in'''
    logging.info("Getting earthquake regions")
    eq_long = earthquake_data['longitude']
    eq_lat = earthquake_data['latitude']
    query = """SELECT r.region_name
                FROM regions r
                WHERE (%s BETWEEN r.min_longitude AND r.max_longitude)
                AND (%s BETWEEN r.min_latitude AND r.max_latitude)"""
    curs.execute(query, (eq_long, eq_lat))
    regions = [result.get('region_name') for result in curs.fetchall()]
    return regions


def get_topics(earthquake_data: dict, curs: cursor) -> list[str]:
    '''Function to generate the specific'''
    logging.info("Loading SNS topics to send to")
    regions = get_earthquake_regions(earthquake_data, curs)
    topics = []
    for region in regions:
        topic_base = re.sub('[,&()]', '', region.replace(' ', '_'))
        topics.append(topic_base+'_0')
        if earthquake_data['magnitude'] >= 4:
            topics.append(topic_base+'_4')
        if earthquake_data['magnitude'] >= 7:
            topics.append(topic_base+'_7')
    return topics


def get_topic_arn(topic_name: str, curs: cursor) -> str:
    '''Function to get the topic arn from the database'''
    query = """SELECT t.topic_arn 
                FROM topics t
                WHERE t.topic_name = %s;"""
    curs.execute(query, (topic_name,))
    topic_arn = curs.fetchone()['topic_arn']
    return topic_arn


def lambda_handler(event, context):
    '''Lambda handler function to be executed within the lambda function on the cloud'''
    load_dotenv()
    rds_connection = get_connection()
    rds_cursor = get_cursor(rds_connection)
    for earthquake in event:
        topics = get_topics(earthquake, rds_cursor)
        sns_client = get_client()
        logging.info("Notifying subscribers")
        for topic in topics:
            topic_arn = get_topic_arn(topic, rds_cursor)
            try:
                sns_client.publish(TopicArn=topic_arn,
                                   Message=f"""Warning! Alert Level {earthquake['alert'].title()}
Earthquake of magnitude {earthquake['magnitude']} {earthquake['place']} ({earthquake['latitude']},\
{earthquake['longitude']}) at {earthquake['time']}""")
            except Exception as e:
                logging.error(
                    f"Could not send notifications to topic: {topic}. Error: {e}")


if __name__ == "__main__":
    lambda_handler([{"longitude": -10.89898,
                    "latitude": 35,
                     "magnitude": 2,
                     "alert": 'red',
                     'place': 'Somewhere',
                     "time": "Noon"}], None)
