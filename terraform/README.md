# 🌍💾 C14 Earthquake Monitor Terraform Guide

This repository contains the infrastructure as code (IaC) for the **C14 Earthquake Monitor ETL Pipeline**, deployed using Terraform. The pipeline includes resources for managing earthquake data, including an RDS database, S3 storage, Lambda functions, a step-function workflow for ETL, and email alert notifications.

## 🗂️ Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Setup and Deployment](#setup-and-deployment)
5. [Future Enhancements](#future-enhancements)
6. [Acknowledgments](#acknowledgments)

---

## 📐 Architecture Overview

The infrastructure comprises the following AWS services:
- 🗄️ **RDS (PostgreSQL)**: Stores processed earthquake data.
- 📦 **S3**: Provides storage for raw and processed data.
- 🪜 **Step Functions**: Orchestrates the ETL pipeline.
- 🔄 **Lambda**: Executes ETL logic.
- ⚙️ **ECS Service**: Runs interactive dashboard as a service.
- ⏰ **EventBridge Scheduler**: Triggers the Lambda function every minute.
- 📧 **SNS (Simple Notification Service)**: Sends email alerts to subscribed users for significant earthquakes.
- 🔐 **IAM Roles & Policies**: Manage permissions for Lambda and EventBridge.
- 📈 **CloudWatch**: Logs Lambda execution and tracks performance.

---

## 📋 Prerequisites

Ensure you have the following:
1. 🛠️ **Terraform v1.x** or higher installed.
2. 💻 **AWS CLI v2** configured with credentials.
3. Access to:
    - 👤 Verified AWS Account
    - 🌐 A VPC with public subnets.

---

## 📂 Project Structure

```plaintext
terraform/
│
├── .pemkey                # Private key needed to connect to EC2 instance (gitignored).
├── api_ec2.tf             # EC2 instance, security group and policies for API.
├── dashboard_ecr.tf       # ECR repository for dashboard app.
├── dashboard_ecs.tf       # Task definition and ECS Service for dashboard.
├── data_upload_ecr.tf     # ECR repository for data upload app.
├── data_upload_lambda.tf  # Lambda and Eventbridge Scheduler configured to trigger RDS to S3 lambda weekly.
├── etl_pipeline_ecr.tf    # ECR repository for ETL pipeline app.
├── etl_pipeline.tf        # Main ETL pipeline resources (RDS, Lambda, EventBridge, IAM).
├── notification_ecr.tf    # ECR repository for earthquake notification app.
├── notification_lambda.tf # Lambda and policies for alert system.
├── s3_bucket.tf           # S3 bucket resource for earthquake data storage.
├── step_function.tf       # Step function to orchestrate notification with policies and role.
├── variables.tf           # Definitions for input variables.
├── terraform.tfvars       # Actual values for variables (gitignored for security).
└── terraform.tfstate      # Terraform state file (also gitignored, but necessary for terraform. Remote backend recommended in future).
```

---

# 🚀 Setup and Deployment

## Clone the repository
Run the following commands to clone the repository and navigate to the `terraform` directory:

```bash
git clone https://github.com/jiuliangut/earthquake-monitor.git
cd c14-earthquake-monitor/terraform
```

### Set up variables

Update `terraform.tfvars` with your specific values:

```hcl
DB_HOST               = "your_db_user"
DB_PORT               = "your_db_port"
DB_PASSWORD           = "your_db_password"
DB_USER               = "your_db_user"
DB_NAME               = "your_db_name"
S3_BUCKET             = "bucket_name"
ACCOUNT_ID            = "your_aws_account_id"
AWS_REGION            = "your_region"
RDS_RESOURCE_ID       = "rds_id"
SSH_ALLOWED_IP        = "your_ip_address"

C14_VPC               = "your_vpc_id"
C14_SUBNET_1          = "your_subnet_id"
C14_SUBNET_2          = "your_subnet_id" - (optional)
C14_SUBNET_3          = "your_subnet_id" - (optional)
C14_CLUSTER           = "your_ecs_cluster"

AWS_ACCESS_KEY_ID     = "your_access_key_id"
AWS_SECRET_ACCESS_KEY = "your_secret_access_key_id"

ETL_ECR_URI           = "latest_etl_image_uri"
DATA_UPLOAD_ECR_URI   = "latest_data_upload_image_uri"
DASHBOARD_ECR_URI     = "latest_dashboard_image_uri"
NOTIFICATION_ECR_URI  = "latest_notification_image_uri"
```

### Initialise Terraform 🛠️

To initialise the Terraform environment, run:

```bash
terraform init
```

### Validate the configuration ✅

Ensure that your Terraform configuration files are valid:

```bash
terraform validate
```
```bash
terraform plan
```

### Deploy the infrastructure 🏗️

Apply the Terraform configuration to deploy the infrastructure:

```bash
terraform apply
```

## EC2 Setup ☁️ 

1. Connect to the EC2 Instance

Use SSH to connect to your EC2 instance:

```bash
ssh -i .pemkey ec2-user@your-ec2-instance-public-ip
```

Replace your-ec2-instance-public-ip with the public IP of your EC2 instance.

2. Install Required Software

```bash
sudo yum install -y git
```

3. Clone the Repository

Clone the project repository from GitHub to the EC2 instance:

```bash
git clone https://github.com/jiuliangut/earthquake-monitor.
```

```bash
cd earthquake-monitor
```

4. Set Up the Environment

Setup python virtual environment and install dependencies

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

5. Create a .env file with the required environment variables for the application.

```bash
cd api
```

```bash
touch .env
```

```bash
nano .env
```

6. Copy over the necessary environment variables and save the changes. 

7. Run API

To run API in the background:

```bash
nohup python3 api.py &
```

### Verify deployment 🔍

After deployment, by going to the AWS User Interface, confirm the following components are correctly set up:

1. 🗄️ **RDS availability and connectivity**  
   Verify the RDS instance is available and can be connected to with the provided credentials.

2. 🪣 **S3 bucket creation**  
   Ensure the S3 bucket `c14-earthquake-monitor-storage` is created successfully.

3. 🔄 **Lambda function and CloudWatch logging**  
   Confirm the Lambda functions are deployed and logging to CloudWatch as expected.

4. 📦 **ECRs have all been created**
   Confirm all four ECRs have been created with their expected names. 
   
5. ☁️ **EC2 availability and connectivity**  
   Verify the EC2 instance is available and can be connected to with the provided credentials.

6. ⚙️ **ECS Service availability**  
   Verify the ECS service is running the task definition and the dashboard is available as a result.

7. 🪜 **Step Function creation**  
   Verify the step function has been created and is correctly orchestrating the main etl pipeline and notification system, after being triggered.