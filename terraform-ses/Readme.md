# Terraform Modules to configure SES

This directory contains two terraform modules that can be used to configure SES domain identities including DKIM verification as well as IAM-Users to send E-Mails via SMTP.

## Terraform Modules

### ses

The ses-module expects an object `domain_configs` as a parameter that may look something like this:

```lang-hcl
domain_configs = {
    "domain_1" = {
        domain_name = "mail.example.com"
        hosted_zone_id = "ABCDEF"
    }
    "domain_2" = {
        domain_name = "another.example.com"
        hosted_zone_id = "SDFKF"
    }
}
```

You can refer to the configurations in the outputs by `domain_1` and `domain_2` in this case.

It has an `domain_identity_arns` output, which returns a map where `domain_1` and `domain_2` would be the keys and the ARNs of the identities the values, e.g.:

```lang-hcl
domain = tomap({
  "domain_1" = "arn:aws:ses:eu-central-1:<some_account_id>:identity/mail.example.com"
  "domain_2" = "arn:aws:ses:eu-central-1:<some_account_id>:identity/another.example.com"
})
```

These can then be used to scope the permissions of the users in the `ses-users` module.

### ses-users

The ses-users module expects a `users` object as a parameter that may look something like this:

```lang-hcl
users = {
    "User for mail.example.com" = {
        iam_username         = "mail.example.com"
        domain_identity_arns = [module.ses_basic.domain_identity_arns["domain_1"]]
    }
    "User for another.example.com" = {
        iam_username         = "another.example.com"
        domain_identity_arns = [module.ses_basic.domain_identity_arns["domain_2"]]
    }
}
```

It creates IAM users with the respective usernames and a set of access keys for them.
The permissions are limited to `ses:SendRawEmail` and the identities to list in the `domain_identity_arns` list. You can also put a wildcard there: `["*"]`.

This module has an output called smtp_credentials that returns the credentials to send messages via SMTP. It's sensitive though, so you need to request the output explicitly.

## Configuration

In the `main.tf` is an example setup for my domain in my account with a single IAM-user that's authorized to send messages.

To configure what's going on, update the locals according to your environment.

```lang-hcl
locals {
  domain         = "mb-trc.de"
  hosted_zone_id = "ZECQVEY17GSI4"
  iam_username_sender = "ses-demo-sender"
}
```

Then run `terraform init` and `terraform apply`.

## Output

After you apply the code, you can fetch the output like this:

```shell
$ tf output smtp_credentials
tomap({
  "Use for Demo" = {
    "smtp_host" = "email-smtp.eu-central-1.amazonaws.com"
    "smtp_password" = "<password>"
    "smtp_port" = 587
    "smtp_use_ssl" = true
    "smtp_username" = "<username>"
  }
})
```

**Note**: Make sure to only send e-mails from the domains you configured here, otherwise SES will block them.
