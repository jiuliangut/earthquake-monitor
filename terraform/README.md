# C14 Earthquake Monitor Terraform Guide

This repository contains the infrastructure as code (IaC) for the **C14 Earthquake Monitor ETL Pipeline**, deployed using Terraform. The pipeline includes resources for managing earthquake data, including an RDS database, S3 storage, Lambda functions, and scheduled ETL jobs.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Setup and Deployment](#setup-and-deployment)
5. [Future Enhancements](#future-enhancements)
6. [Acknowledgments](#acknowledgments)

---

## Architecture Overview

The infrastructure comprises the following AWS services:
- **RDS (PostgreSQL)**: Stores earthquake data.
- **S3**: Provides storage for raw and processed data.
- **Lambda**: Executes ETL logic.
- **EventBridge Scheduler**: Triggers the Lambda function every minute.
- **IAM Roles & Policies**: Manage permissions for Lambda and EventBridge.
- **CloudWatch**: Logs Lambda execution and tracks performance.

---

## Prerequisites

Ensure you have the following:
1. **Terraform v1.x** or higher installed.
2. **AWS CLI v2** configured with credentials.
3. Access to:
    - A VPC with public subnets.

---

## Project Structure

```plaintext
terraform/
│
├── etl_pipeline.tf        # Main ETL pipeline resources (RDS, Lambda, EventBridge, IAM).
├── s3_bucket.tf           # S3 bucket resource for earthquake data storage.
├── dashboard_ecr.tf       # ECR repository and lifecycle policy for dashboard app.
├── data_upload_ecr.tf     # ECR repository and lifecycle policy for data upload app.
├── etl_pipeline_ecr.tf    # ECR repository and lifecycle policy for ETL pipeline app.
├── variables.tf           # Definitions for input variables.
├── terraform.tfvars       # Actual values for variables (gitignored for security).
└── terraform.tfstate      # Terraform state file (also gitignored, but necessary for terraform. Remote backend recommended in future).
```

---

# Setup and Deployment

## Clone the repository
Run the following commands to clone the repository and navigate to the `terraform` directory:

```bash
git clone https://github.com/jiuliangut/earthquake-monitor.git
cd c14-earthquake-monitor/terraform
```

### Set up variables

Update `terraform.tfvars` with your specific values:

```hcl
DB_USER       = "your_db_user"
DB_PASSWORD   = "your_db_password"
DB_NAME       = "your_db_name"
C14_VPC       = "your_vpc_id"
C14_SUBNET_1  = "your_subnet_id"
ETL_ECR_URI   = "your_ecr_repo_uri"
DATA_UPLOAD_ECR_URI = "your_ecr_repo_uri"
DASHBOARD_ECR_URI = "your_ecr_repo_uri"
```

### Initialise Terraform

To initialise the Terraform environment, run:

```bash
terraform init
```

### Validate the configuration

Ensure that your Terraform configuration files are valid:

```bash
terraform validate
```

### Deploy the infrastructure

Apply the Terraform configuration to deploy the infrastructure:

```bash
terraform apply
```

### Verify deployment

After deployment, confirm the following components are correctly set up:

1. **RDS availability and connectivity**  
   Verify the RDS instance is available and can be connected to with the provided credentials.

2. **S3 bucket creation**  
   Ensure the S3 bucket `c14-earthquake-monitor-storage` is created successfully.

3. **Lambda function and CloudWatch logging**  
   Confirm the Lambda function is deployed and logging to CloudWatch as expected.

4. **ECRs have all been created**
    Confirm all three ECRs have been created with their expected names. 
