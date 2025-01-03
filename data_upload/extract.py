"""Script to extract earthquake data from RDS and upload to S3 bucket as PDF"""
import os
import logging
import unicodedata
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
QUERY = """
        SELECT *
        FROM earthquakes AS e
        JOIN alerts AS a ON e.alert_id = a.alert_id
        JOIN networks AS n ON e.network_id = n.network_id
        JOIN magnitude AS m ON e.magnitude_id = m.magnitude_id;
        """

COLUMNS = ['place', 'time', 'magnitude', 'alert_type', 'felt_report_count',
           'cdi', 'latitude', 'longitude', 'depth', 'magnitude_type',
           'network_name']

PDF_FILE = f"""/tmp/{(datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')}-data.pdf"""

COL_WIDTHS = [
    170,  # place
    80,   # time
    65,   # magnitude
    40,   # alert type
    50,   # felt report count
    40,   # cdi
    70,   # latitude
    70,   # longitude
    42,   # depth
    64,   # magtype
    52   # network name
]

COLUMN_NAME_MAP = {
    'time': 'Time',
    'place': 'Place',
    'magnitude': 'Magnitude',
    'felt_report_count': 'Felt Report Count',
    'cdi': 'CDI',
    'latitude': 'Latitude',
    'longitude': 'Longitude',
    'depth': 'Depth',
    'alert_type': 'Alert Type',
    'magnitude_type': 'Magnitude Type',
    'network_name': 'Network Name',
}


def get_connection() -> connection:
    """Gets connection to database"""
    return psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )


def normalise_text(text: str) -> str:
    """Converts special Unicode characters to plain ASCII equivalents"""
    if not isinstance(text, str):
        return text
    normalised = unicodedata.normalize('NFD', text)
    ascii_text = re.sub(r'[\u0300-\u036f]', '', normalised)
    return ascii_text


def extract_data() -> pd.DataFrame:
    """Extracts data from the database and prepares it for PDF generation"""
    conn = None
    try:
        conn = get_connection()
        logging.info("Executing query...")
        earthquakes = pd.read_sql(QUERY, conn)
        earthquakes = earthquakes[COLUMNS]
        earthquakes = earthquakes.rename(columns=COLUMN_NAME_MAP)
        earthquakes['Depth'] = earthquakes['Depth'].apply(
            lambda x: f"{x:.2f}" if pd.notnull(x) else x)
        earthquakes['Latitude'] = earthquakes['Latitude'].apply(
            lambda x: f"{x:.6f}" if pd.notnull(x) else x)
        earthquakes['Longitude'] = earthquakes['Longitude'].apply(
            lambda x: f"{x:.6f}" if pd.notnull(x) else x)
        earthquakes['Place'] = earthquakes['Place'].apply(
            lambda x: normalise_text(str(x)) if pd.notnull(x) else x)
        earthquakes["Time"] = earthquakes["Time"].apply(
            lambda x: pd.to_datetime(x).strftime(
                "%Y-%m-%d %H:%M") if pd.notnull(x) else x
        )
        return earthquakes

    except Exception as e:
        logging.error("Error during data extraction: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def compute_summary(data: pd.DataFrame) -> list:
    """Calculates summary analytics from earthquake dataframe"""
    highest_magnitude = data.loc[data['Magnitude'].idxmax()]
    number_of_earthquakes = len(data)
    average_magnitude = data['Magnitude'].mean()

    summary = [
        ["Weekly Summary"],
        ["Number of Earthquakes", number_of_earthquakes],
        ["Average Magnitude", f"{average_magnitude:.2f}"],
        ["\n Strongest Earthquake \n",
            f"Magnitude: {highest_magnitude['Magnitude']} \n Location: {highest_magnitude['Place']} \n Time: {highest_magnitude['Time']}"]
    ]
    return summary


def make_pdf(data: pd.DataFrame) -> None:
    """Generates a PDF from the provided dataframe"""
    logging.info("Writing data to PDF: %s", PDF_FILE)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontName="Helvetica-Bold",
        fontSize=18,
        alignment=1,
        spaceAfter=20,
    )
    title_text = Paragraph("Weekly Earthquake Summary", title_style)
    icon_path = "../diagrams/geovigil_logo.png"
    icon = Image(icon_path, width=1.0 * inch,
                 height=1.0 * inch)

    title = Table(
        [[icon, title_text]],
        colWidths=[0.6 * inch, None],
        style=[
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ],
    )

    header_styles = styles['BodyText']
    header_styles.fontName = "Helvetica-Bold"
    table_data = [
        [Paragraph(str(col), header_styles) for col in data.columns]
    ]
    for row in data.values.tolist():
        wrapped_row = [Paragraph(str(cell), styles["BodyText"])
                       for cell in row]
        table_data.append(wrapped_row)

    # Summary table
    summary_data = compute_summary(data)
    summary_table = Table(summary_data, colWidths=[150, 350])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.olive),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    summary_table.setStyle(style)

    # Data table
    pdf = SimpleDocTemplate(PDF_FILE, pagesize=landscape(letter))
    data_table = Table(table_data, colWidths=COL_WIDTHS)
    data_table.setStyle(style)
    line_space = Spacer(width=0, height=20)
    pdf.build([title, summary_table, line_space, data_table])
    logging.info("Data successfully written to %s", PDF_FILE)


def get_client():
    """Returns S3 client using env credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"))


def upload_to_s3():
    """Uploads pdf file to S3 bucket and clears temp file"""
    s3_client = get_client()
    bucket_name = os.getenv("BUCKET_NAME")
    s3_key = f"""{(datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')}-data.pdf"""
    try:
        logging.info("Uploading to bucket")
        s3_client.upload_file(
            Filename=PDF_FILE, Bucket=bucket_name, Key=s3_key)
        os.remove(PDF_FILE)
        logging.info("Upload successful")
    except Exception as e:
        logging.info("Failed to upload file to S3: %s", e)
        raise


def lambda_handler(event, context):
    """For AWS lambda function"""
    try:
        load_dotenv()
        earthquakes = extract_data()
        make_pdf(earthquakes)
        upload_to_s3()
        return {"statusCode": 200, "body": "Data upload pipeline executed successfully"}
    except Exception as e:
        logging.info("Execution error: %s", e)
        return {"statusCode": 500, "body": f"Error occurred: {e}"}


if __name__ == "__main__":
    try:
        load_dotenv()
        earthquakes = extract_data()
        make_pdf(earthquakes)
        upload_to_s3()
    except Exception as e:
        logging.info("Execution error: %s", e)
