data "aws_region" "current" {}

locals {
  smtp_credentials = { for key in keys(var.users) : key => {
    smtp_host     = "email-smtp.${data.aws_region.current.name}.amazonaws.com"
    smtp_port     = 587
    smtp_use_ssl  = true
    smtp_username = aws_iam_access_key.this[key].id
    smtp_password = aws_iam_access_key.this[key].ses_smtp_password_v4
  } }
}

output "smtp_credentials" {
  value     = tomap(local.smtp_credentials)
  sensitive = true
}
