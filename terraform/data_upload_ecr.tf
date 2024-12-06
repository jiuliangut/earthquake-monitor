resource "aws_ecr_repository" "c14_earthquake_monitor_data_upload_ecr" {
  name                 = "c14_earthquake_monitor_data_upload_ecr"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
