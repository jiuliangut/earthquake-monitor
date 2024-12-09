data "aws_ecs_cluster" "cluster" {
  cluster_name = var.C14_CLUSTER
}

resource "aws_iam_role" "ecs_service_role" {
  name               = "c14-earthquake-monitor-ecs-service-role"
  lifecycle {
    prevent_destroy = false
  }
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect    : "Allow",
        Principal : {
          Service : "ecs-tasks.amazonaws.com"
        },
        Action    : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_service_s3_policy" {
  name        = "c14-earthquake-monitor-ecs-service-s3-policy"
  description = "Allow ECS service to connect to s3 data for streamlit"
  lifecycle {
    prevent_destroy = false
  }

  policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect   : "Allow",
        Action   : [
          "s3:GetObject"
        ],
        Resource : "arn:aws:s3:::c14-earthquake-monitor-storage/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_service_s3_policy_attachment" {
  role       = aws_iam_role.ecs_service_role.name
  policy_arn = aws_iam_policy.ecs_service_s3_policy.arn
}

resource "aws_cloudwatch_log_group" "dashboard_log_group" {
  name              = "/ecs/c14-earthquake-monitor-dashboard"
  lifecycle {
    prevent_destroy = false
  }
  retention_in_days = 7
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c14_earthquake_monitor_dashboard" {
  family                   = "c14-earthquake-monitor-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "1024"
  task_role_arn            = aws_iam_role.ecs_service_role.arn
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name        = "c14_earthquake_monitor_dashboard_ecr" 
      image       = var.DASHBOARD_ECR_URI
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DB_HOST", value = var.DB_HOST },
        { name = "DB_PORT", value = var.DB_PORT },
        { name = "DB_USER", value = var.DB_USER },
        { name = "DB_NAME", value = var.DB_NAME },
        { name = "DB_PASSWORD", value = var.DB_PASSWORD },
        { name = "AWS_ACCESS_KEY_ID", value = var.AWS_ACCESS_KEY_ID},
        { name = "AWS_SECRET_ACCESS_KEY", value = var.AWS_SECRET_ACCESS_KEY},
        { name = "AWS_REGION", value = var.AWS_REGION}
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/c14-earthquake-monitor-dashboard"
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }
}

resource "aws_security_group" "ecs_service_sg" {
  name        = "c14-earthquake-monitor-streamlit-sg"
  description = "Allow access to Streamlit app"
  vpc_id      = var.C14_VPC

  lifecycle {
    prevent_destroy = false
  }

  ingress {
      description = "Allows access to streamlit"  
      from_port   = 8501
      to_port     = 8501
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }

  egress {
      description = "Allows all outbound traffic"  
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_ecs_service" "service" {
  name            = "c14-earthquake-monitor-dashboard-service"
  cluster         = data.aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.c14_earthquake_monitor_dashboard.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [var.C14_SUBNET_1, var.C14_SUBNET_2, var.C14_SUBNET_3]
    security_groups  = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true
  }
}