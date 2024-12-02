provider "aws" {
    region = "eu-west-2"
}

# ------ Earthquake RDS SETUP

# Security group for rds
resource "aws_security_group" "c14-earthquake-monitor-db-sg" {
    name = "c14-earthquake-monitor-db-sg"
    description = "Allows access to PostgreSQL from anywhere"
    vpc_id = var.C14_VPC

    ingress = {
        description = "PostgreSQL"
        from_port = var.DB_PORT
        to_port = var.DB_PORT
        protocol = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
    }

    egress = {
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