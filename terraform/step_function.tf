resource "aws_iam_role" "c14_earthquake_monitor_step_function_role" {
  name = "c14-earthquake-monitor-step-function-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_policy" "c14_step_function_policy" {
  name = "c14-earthquake-monitor-step-function-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          "arn:aws:lambda:eu-west-2:129033205317:function:c14-earthquake-monitor-etl-lambda-function-tf:$LATEST",
          "arn:aws:lambda:eu-west-2:129033205317:function:c14-earthquake-notification-lambda:$LATEST"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = [
          "arn:aws:sns:eu-west-2:${var.ACCOUNT_ID}:*" 
        ]
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "attach_step_function_policy" {
  role       = aws_iam_role.c14_earthquake_monitor_step_function_role.name
  policy_arn = aws_iam_policy.c14_step_function_policy.arn
}

resource "aws_sfn_state_machine" "c14_earthquake_monitor_step_function" {
  name = "c14-earthquake-monitor-step-function"
  role_arn = aws_iam_role.c14_earthquake_monitor_step_function_role.arn
  definition = jsonencode({
  "QueryLanguage": "JSONPath",
  "Comment": "A description of my state machine",
  "StartAt": "Run Pipeline",
  "States": {
    "Run Pipeline": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:c14-earthquake-monitor-etl-lambda-function-tf:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Choice"
    },
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "And": [
            {
              "Not": {
                "Variable": "$.body",
                "StringEquals": "No new earthquake data"
              }
            },
            {
              "Variable": "$.status_code",
              "NumericEquals": 200
            }
          ],
          "Next": "Run Notifications"
        }
      ],
      "Default": "Pass"
    },
    "Pass": {
      "Type": "Pass",
      "End": true
    },
    "Run Notifications": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:c14-earthquake-notification-lambda:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Success",
      "InputPath": "$.body"
    },
    "Success": {
      "Type": "Succeed"
    }
  }
})
}