# resource "aws_ecr_repository" "c14_earthquake_monitor_etl_ecr" {
#   name                 = "c14_earthquake_monitor_etl_ecr"
#   image_tag_mutability = "MUTABLE"

#   image_scanning_configuration {
#     scan_on_push = true
#   }
# }

# resource "aws_ecr_lifecycle_policy" "c14_earthquake_monitor_etl_ecr_lifecycle_policy" {
#   repository = aws_ecr_repository.c14_earthquake_monitor_etl_ecr.name

#   policy = <<EOF
# {
#     "rules": [
#         {
#             "rulePriority": 1,
#             "description": "Keep last 30 images",
#             "selection": {
#                 "tagStatus": "tagged",
#                 "countType": "imageCountMoreThan",
#                 "countNumber": 30
#             },
#             "action": {
#                 "type": "expire"
#             }
#         }
#     ]
# }
# EOF
# }