## 🌍📄 Earthquake Data Extraction and S3 Upload Script


A Python script to extract earthquake data from an RDS database, generate a PDF report, and upload it to an S3 bucket.


## 📖 Introduction
This script extracts earthquake data from an Amazon RDS database, formats it into a well-structured PDF report, and uploads the report to an AWS S3 bucket. It can be run locally or as an AWS Lambda function for automation.


## ✨ Features
- 📊 Fetches earthquake data using a SQL query that joins multiple related tables.
- 🛠️ Processes the extracted data into a pandas DataFrame and applies formatting.
- 🖨️ Generates a visually appealing PDF report using ReportLab.
- ☁️ Uploads the generated PDF report to a specified S3 bucket.


## ⚙️ Configuration


Set up the environment variables in a `.env` file:


```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
ACCESS_KEY_ID=your_aws_access_key
SECRET_ACCESS_KEY=your_aws_secret_access_key
BUCKET_NAME=your_s3_bucket_name
```


## 🚀 Usage
🔧 Local Execution
Run the script locally:


```python3 extract.py```


This will:


- Extract data from the database.
- Generate a PDF file in the `/tmp` directory.
- Upload the PDF to the configured S3 bucket.


🖥️ **AWS Lambda Execution**


Deploy the script as an AWS Lambda function:


- 📦 Package the script with dependencies (e.g., using zip or AWS SAM).
- 🚀 Deploy it to Lambda with the correct IAM role and environment variables.


⚡ The Lambda function will automatically execute the pipeline when triggered.

