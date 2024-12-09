# 🔔 Earthquake Notification Module

This module handles the processing of earthquake data, determines the affected regions, and sends notifications to subscribers via AWS SNS. It integrates AWS services with a PostgreSQL database (RDS) for managing subscription data.

---

## 🌟 Features

- Database Integration: Connects to an RDS PostgreSQL database to retrieve regions and SNS topic ARNs.
- SNS Notification: Publishes earthquake alerts to relevant SNS topics based on magnitude and location.
- AWS Environment Setup: Securely integrates with AWS services using environment variables.
  
---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Required packages:
  
    ```pip install -r requirements.txt```

### Environment Variables
Ensure the following are set in your ```.env``` file:

```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
ACCESS_KEY_ID=your_aws_access_key
SECRET_ACCESS_KEY=your_aws_secret_access_key
```

---

## 📋 How It Works
### 1️⃣ Database Connection
The script establishes a connection to the RDS PostgreSQL database to:

- Retrieve earthquake-affected regions based on latitude and longitude.
- Map SNS topics to the earthquake event.
  
### 2️⃣ SNS Notification
The AWS SNS client publishes alerts to topics corresponding to:
- Affected regions.
- Minimum magnitude thresholds (0, 4, 7).

### 3️⃣ Lambda Deployment
The ```lambda_handler()``` function is designed to run as an AWS Lambda function, triggered by events containing earthquake data.


## 🛡️ Error Handling
| **Error Type**                  | **Description**                                       | **Resolution**                                   |
|---------------------------------|-------------------------------------------------------|-------------------------------------------------|
| `KeyError`                      | Raised when an expected environment variable is missing. | Ensure all required variables are set in `.env`. |
| `OperationalError`              | Raised when database connection fails.               | Verify database credentials and network access. |
| `boto3.exceptions.ClientError`  | Raised when SNS operations fail.                     | Check SNS topic permissions and AWS credentials. |
| ```Generic Exception```               | Logs unexpected errors during execution.             | Check the logs for detailed error messages.     |

