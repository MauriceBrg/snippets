variable "users" {
  type = map(object({
    iam_username         = string
    domain_identity_arns = list(string)
  }))
}
