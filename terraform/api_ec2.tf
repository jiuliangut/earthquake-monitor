# Security Group for API EC2 Instance
resource "aws_security_group" "c14-earthquake-api-sg" {
  name        = "c14-earthquake-api-sg"
  description = "Allow access to API on HTTP/HTTPS and SSH"
  vpc_id      = "vpc-0344763624ac09cb6"

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Flask API (port 5000)"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
  }

  ingress {
    description = "Allow SSH from trusted IP range"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.SSH_ALLOWED_IP]  
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allows all outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Role for EC2 Instance to Access S3 and RDS
resource "aws_iam_role" "c14-earthquake-api-ec2-role" {
  name = "c14-earthquake-api-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy to Allow Access to S3 and RDS
resource "aws_iam_policy" "c14-earthquake-api-ec2-policy" {
  name = "c14-earthquake-api-ec2-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "arn:aws:s3:::${var.S3_BUCKET}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["rds:DescribeDBInstances", "rds-db:connect"]
        Resource = "arn:aws:rds-db:eu-west-2:${var.ACCOUNT_ID}:dbuser:${var.RDS_RESOURCE_ID}/${var.DB_USER}"
      }
    ]
  })
}

# Attach Policy to Role
resource "aws_iam_role_policy_attachment" "c14_earthquake_api_ec2_policy_attachment" {
  role       = aws_iam_role.c14-earthquake-api-ec2-role.name
  policy_arn = aws_iam_policy.c14-earthquake-api-ec2-policy.arn
}

# Instance Profile for EC2 Role
resource "aws_iam_instance_profile" "c14_earthquake_api_ec2_instance_profile" {
  name = "c14-earthquake-api-instance-profile"
  role = aws_iam_role.c14-earthquake-api-ec2-role.name
}

# EC2 instance for hosting the API
resource "aws_instance" "c14-earthquake-api-ec2" {
  ami           = "ami-0acc77abdfc7ed5a6"
  instance_type = "t2.nano"
  subnet_id     = "subnet-0497831b67192adc2" 
  associate_public_ip_address = true 

  vpc_security_group_ids = [aws_security_group.c14-earthquake-api-sg.id]

  key_name = "c14-krish-seechurn-key2"

  iam_instance_profile = aws_iam_instance_profile.c14_earthquake_api_ec2_instance_profile.name

  tags = {
    Name = "c14-earthquake-api-ec2"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3 python3-pip
              EOF
}
