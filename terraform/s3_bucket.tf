# resource "aws_s3_bucket" "c14-earthquake-monitor-storage" {
#   bucket        = "c14-earthquake-monitor-storage"
#   force_destroy = "false"
#   acl = "private"

#   object_lock_enabled = "false"
#   request_payer       = "BucketOwner"

#   server_side_encryption_configuration {
#     rule {
#       apply_server_side_encryption_by_default {
#         sse_algorithm = "AES256"
#       }

#       bucket_key_enabled = "true"
#     }
#   }

#   versioning {
#     enabled    = "false"
#     mfa_delete = "false"
#   }
# }