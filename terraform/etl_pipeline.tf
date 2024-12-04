provider "aws" {
    region = "eu-west-2"
}

# ------ Earthquake RDS SETUP

# Security group for rds
resource "aws_security_group" "c14-earthquake-monitor-db-sg" {
    name = "c14-earthquake-monitor-db-sg"
    description = "Allows access to PostgreSQL from anywhere"
    vpc_id = var.C14_VPC

    ingress {
        description = "PostgreSQL"
        from_port = var.DB_PORT
        to_port = var.DB_PORT
        protocol = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = [ "0.0.0.0/0"]
    }
}

# RDS instance
resource "aws_db_instance" "c14-earthquake-monitor-db" {
    allocated_storage    = 20
    engine               = "postgres"
    engine_version       = "16.2"
    instance_class       = "db.t3.micro"
    db_name              = var.DB_NAME
    identifier           = "c14-earthquake-monitor-db"
    username             = var.DB_USER
    password             = var.DB_PASSWORD
    publicly_accessible = true
    skip_final_snapshot = true
    performance_insights_enabled = false

    db_subnet_group_name = "c14-public-subnet-group"

    vpc_security_group_ids = [ aws_security_group.c14-earthquake-monitor-db-sg.id ]

    tags = {
      "Name" = "c14-earthquake-monitor-db"
    }
}

# --------------- EARTHQUAKE ETL: LAMBDA & EVENT BRIDGE

# IAM Role for Lambda execution
resource "aws_iam_role" "c14-earthquake-monitor-etl-lambda_execution_role-tf" {
  name = "c14-earthquake-monitor-etl-lambda_execution_role-tf"

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

# IAM Policy for Lambda execution role
resource "aws_iam_role_policy" "c14-earthquake-monitor-etl-lambda_execution_policy-tf" {
  name = "c14-earthquake-monitor-etl-lambda_execution_policy-tf"
  role = aws_iam_role.c14-earthquake-monitor-etl-lambda_execution_role-tf.id

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
        Resource = "*"
      },
      {
        Action   = "dynamodb:Query"
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/c14-earthquake-monitor-etl-lambda-function-tf"
  retention_in_days = 7
}


resource "aws_lambda_function" "c14-earthquake-monitor-etl-lambda-function-tf" {
  role          = aws_iam_role.c14-earthquake-monitor-etl-lambda_execution_role-tf.arn
  function_name = "c14-earthquake-monitor-etl-lambda-function-tf"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = var.ETL_ECR_URI

  timeout       = 720
  depends_on    = [aws_cloudwatch_log_group.lambda_log_group]

  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY,
      SECRET_ACCESS_KEY = var.AWS_SECRET_KEY,
      DB_HOST           = var.DB_HOST,
      DB_NAME           = var.DB_NAME,
      DB_USER           = var.DB_USER,
      DB_PASSWORD       = var.DB_PASSWORD,
      DB_PORT           = var.DB_PORT
    }
  }
    logging_config {
    log_format = "Text"
    log_group  = "/aws/lambda/c14-earthquake-monitor-etl-lambda-function-tf"
  }

  tracing_config {
    mode = "PassThrough"
  }
}

# Event bridge schedule: 
# IAM Role for AWS Scheduler
resource "aws_iam_role" "c14-earthquake-monitor-etl-scheduler_execution_role-tf" {
  name = "c14-runtime-earthquake-monitor-etl-scheduler_execution_role-tf"

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

resource "aws_iam_role_policy" "c14-earthquake-monitor-etl-scheduler_execution_policy-tf" {
  name = "c14-earthquake-monitor-etl-scheduler_execution_policy-tf"
  role = aws_iam_role.c14-earthquake-monitor-etl-scheduler_execution_role-tf.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.c14-earthquake-monitor-etl-lambda-function-tf.arn
      }
    ]
  })
}

# AWS Scheduler Schedule: every minute
resource "aws_scheduler_schedule" "c14-earthquake-monitor-etl-schedule-tf" {
  name                         = "c14-earthquake-monitor-etl-schedule-tf"
  schedule_expression          =  "cron(* * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c14-earthquake-monitor-etl-lambda-function-tf.arn
    role_arn = aws_iam_role.c14-earthquake-monitor-etl-scheduler_execution_role-tf.arn
  }
}