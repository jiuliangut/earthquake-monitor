# resource "aws_ecr_repository" "c14_earthquake_monitor_dashboard_ecr" {
#   name                 = "c14_earthquake_monitor_dashboard_ecr"
#   image_tag_mutability = "MUTABLE"

#   image_scanning_configuration {
#     scan_on_push = true
#   }
# }

# resource "aws_ecr_lifecycle_policy" "c14_earthquake_monitor_dashboard_ecr_lifecycle_policy" {
#   repository = aws_ecr_repository.c14_earthquake_monitor_dashboard_ecr.name

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