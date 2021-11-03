# Basic Domain Identities

resource "aws_ses_domain_identity" "domain_identities" {
  for_each = var.domain_configs

  domain = each.value.domain_name
}

# Waiter for verifications
resource "aws_ses_domain_identity_verification" "example_verification" {
  for_each = var.domain_configs

  domain = aws_ses_domain_identity.domain_identities[each.key].id

  depends_on = [aws_route53_record.domain_identity_verifications]
}


# Generate the DKIM-Tokens
resource "aws_ses_domain_dkim" "domain_dkim" {
  for_each = var.domain_configs

  domain = aws_ses_domain_identity.domain_identities[each.key].domain
}
