# IAM Role for Lambda Execution
resource "aws_iam_role" "c14_lambda_execution_role" {
  name = "c14-earthquake-monitor-etl-lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for RDS and S3 Access
resource "aws_iam_role_policy" "c14_lambda_execution_policy" {
  name = "c14-earthquake-monitor-etl-lambda_execution_policy"
  role = aws_iam_role.c14_lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = ["rds:DescribeDBInstances", "rds-db:connect"],
        Effect   = "Allow"
        Resource = "arn:aws:rds-db:eu-west-2:${var.ACCOUNT_ID}:dbuser:${var.RDS_RESOURCE_ID}/${var.DB_USER}"
      },
      {
        Action   = ["s3:PutObject", "s3:GetObject"],
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${var.S3_BUCKET}/*"
      }
    ]
  })
}

# Lambda Function using Docker Image
resource "aws_lambda_function" "c14-earthquake-report-lambda" {
  function_name    = "c14-earthquake-report-lambda"
  role             = aws_iam_role.c14_lambda_execution_role.arn
  package_type     = "Image"
  image_uri        = "${var.ETL_ECR_URI}:latest" #placeholder until we get the actual image uri
  timeout          = 900 # 15 minutes
  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY
      SECRET_ACCESS_KEY = var.AWS_SECRET_KEY
      ACCOUNT_ID        = var.ACCOUNT_ID
      RDS_RESOURCE_ID   = var.RDS_RESOURCE_ID
      DB_HOST           = var.DB_HOST
      DB_NAME           = var.DB_NAME
      DB_USER           = var.DB_USER
      DB_PASSWORD       = var.DB_PASSWORD
      DB_PORT           = var.DB_PORT
      S3_BUCKET         = var.S3_BUCKET
    }
  }
}

# IAM Role for Scheduler
resource "aws_iam_role" "c14_scheduler_execution_role" {
  name = "c14-earthquake-monitor-etl-scheduler_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

# Policy to Allow Scheduler to Invoke Lambda
resource "aws_iam_role_policy" "c14_scheduler_execution_policy" {
  name = "c14-earthquake-monitor-etl-scheduler_execution_policy"
  role = aws_iam_role.c14_scheduler_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.c14-earthquake-report-lambda.arn # 
      }
    ]
  })
}

# EventBridge Schedule
resource "aws_scheduler_schedule" "c14-earthquake-report-schedule" {
  name                         = "c14-earthquake-report-schedule"
  schedule_expression          = "cron(1 0 ? * MON *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c14-earthquake-report-lambda.arn #
    role_arn = aws_iam_role.c14_scheduler_execution_role.arn
  }
}