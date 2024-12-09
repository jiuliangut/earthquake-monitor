variable "DB_USER" {
    type = string
}
variable "DB_PASSWORD"{
    type = string
}
variable "DB_NAME" {
    type = string
}
variable "DB_HOST"{
    type = string
}
variable "DB_PORT"{
    type = string
}

variable "S3_BUCKET" {
    type = string
}

variable "C14_VPC"{
    type = string
}
variable "C14_SUBNET_1"{
    type = string
}
variable "C14_SUBNET_2"{
    type = string
}
variable "C14_SUBNET_3"{
    type = string
}
variable C14_CLUSTER{
    type = string
}

variable "AWS_ACCESS_KEY_ID" {
  type = string
}
variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}
variable "AWS_REGION" {
    type = string
}

variable "ETL_ECR_URI" {
    type = string
}

variable "DATA_UPLOAD_ECR_URI" {
    type = string
}

variable "DASHBOARD_ECR_URI" {
    type = string
}

variable "ACCOUNT_ID" {
    type = string
}

variable "RDS_RESOURCE_ID" {
    type = string
}

variable "SSH_ALLOWED_IP" {
  description = "IP address allowed to SSH into the EC2 instance"
  type        = string
  default     = "0.0.0.0/0"  # Optional: default value can be overwritten in tfvars
}

variable "NOTIFICATION_ECR_URI" {
  description = "Notification script image ECR URI"
  type = string
}