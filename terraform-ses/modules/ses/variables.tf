variable "domain_configs" {
  type = map(object({
    domain_name    = string
    hosted_zone_id = string
    })
  )
}
