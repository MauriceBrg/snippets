output "domain_identity_arns" {
  value = tomap({ for key, value in aws_ses_domain_identity.domain_identities : key => value.arn })
}
