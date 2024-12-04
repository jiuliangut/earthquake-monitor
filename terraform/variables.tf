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

variable "AWS_ACCESS_KEY" {
  type = string
}
variable "AWS_SECRET_KEY" {
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