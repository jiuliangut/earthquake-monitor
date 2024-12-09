resource "aws_iam_role" "c14_earthquake_notification_lambda_role" {
  name = "c14-earthquake-notification-lambda-role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "c14_earthquake_notification_lambda_policy" {
  name = "c14-earthquake-notification-lambda-policy"
  role = aws_iam_role.c14_earthquake_notification_lambda_role.id
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "logs:CreateLogGroup",
        "Resource": "arn:aws:logs:eu-west-2:${var.ACCOUNT_ID}:*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": [
          aws_cloudwatch_log_group.c14_earthquake_notification_lambda_logs.arn
        ]
      },
            {
        "Effect": "Allow",
        "Action": "sns:Publish",
        "Resource": "arn:aws:sns:eu-west-2:${var.ACCOUNT_ID}:*"
      }
    ]
  })
}

resource "aws_lambda_function" "c14_earthquake_notification_lambda" {
  function_name = "c14-earthquake-notification-lambda"
  role          = aws_iam_role.c14_earthquake_notification_lambda_role.arn
  package_type  = "Image"
  image_uri     = var.NOTIFICATION_ECR_URI
  timeout       = 900
  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_NAME     = var.DB_NAME
      DB_USER     = var.DB_USER
      DB_PASSWORD = var.DB_PASSWORD
      DB_PORT     = var.DB_PORT
    }
  }
}

resource "aws_cloudwatch_log_group" "c14_earthquake_notification_lambda_logs" {
  name              = "/aws/lambda/c14-earthquake-notification-lambda"
  retention_in_days = 14
}