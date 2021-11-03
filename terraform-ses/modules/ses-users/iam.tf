resource "aws_iam_user" "this" {
  for_each = var.users

  name = each.value.iam_username
}

resource "aws_iam_access_key" "this" {
  for_each = var.users

  user = aws_iam_user.this[each.key].name
}

data "aws_iam_policy_document" "ses_send_access" {

  for_each = var.users

  statement {
    effect = "Allow"

    actions = [
      "ses:SendRawEmail",
    ]

    resources = each.value.domain_identity_arns
  }
}

resource "aws_iam_user_policy" "this" {

  for_each = var.users

  user = aws_iam_user.this[each.key].name

  policy = data.aws_iam_policy_document.ses_send_access[each.key].json
}
