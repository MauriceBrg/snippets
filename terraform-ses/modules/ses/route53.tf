resource "aws_route53_record" "domain_identity_verifications" {
  for_each = var.domain_configs

  zone_id = each.value.hosted_zone_id
  name    = "_amazonses.example.com"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.domain_identities[each.key].verification_token]
}

# For each domain we have to create three DKIM-Records

locals {
  dkim_key_values = { for p in setproduct(keys(var.domain_configs), [0, 1, 2]) : "${p[0]}/${p[1]}" => {
    domain_key = p[0]
    index      = p[1]
    }
  }
}

resource "aws_route53_record" "dkim_records" {
  for_each = local.dkim_key_values
  zone_id  = var.domain_configs[each.value.domain_key].hosted_zone_id
  name     = "${element(aws_ses_domain_dkim.domain_dkim[each.value.domain_key].dkim_tokens, each.value.index)}._domainkey"
  type     = "CNAME"
  ttl      = "600"
  records  = ["${element(aws_ses_domain_dkim.domain_dkim[each.value.domain_key].dkim_tokens, each.value.index)}.dkim.amazonses.com"]
}
