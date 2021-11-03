terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>3.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

locals {
  domain         = "mb-trc.de"
  hosted_zone_id = "ZECQVEY17GSI4"

  iam_username_sender = "ses-demo-sender"
}

module "ses_basic" {
  source = "./modules/ses"

  domain_configs = {
    "${local.domain}" = {
      domain_name    = local.domain
      hosted_zone_id = local.hosted_zone_id
    }
  }
}

module "ses_users" {
  source = "./modules/ses-users"

  users = {
    "Use for Demo" = {
      iam_username         = local.iam_username_sender
      domain_identity_arns = [module.ses_basic.domain_identity_arns[local.domain]]
    }
  }
}

output "smtp_credentials" {
  value     = module.ses_users.smtp_credentials
  sensitive = true
}
