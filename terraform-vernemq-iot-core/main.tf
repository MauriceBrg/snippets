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

resource "aws_s3_bucket" "target_bucket" {
  bucket_prefix = "iot-target-bucket-"
}

resource "aws_kinesis_firehose_delivery_stream" "s3_stream" {
  name        = "terraform-kinesis-firehose-extended-s3-test-stream"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.target_bucket.arn

    # TODO: Conversion to Parquet

  }
}

resource "aws_iam_role" "firehose_role" {
  name = "firehose_test_role"

  inline_policy {
    name = "AllowS3Put"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [{
        "Action" : ["s3:Put*"],
        "Effect" : "Allow",
        "Resource" : "*"
      }]
    })
  }

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iot_policy" "pubsub" {
  name = "PubSubToAnyTopic"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "iot:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iot_certificate" "cert" {
  active = true
}

resource "aws_iot_policy_attachment" "att" {
  policy = aws_iot_policy.pubsub.name
  target = aws_iot_certificate.cert.arn
}

resource "aws_iot_topic_rule" "rule" {
  name        = "PushToKinesisFirehose"
  description = "Push a subset to kinesis firehose"
  enabled     = true
  sql         = "SELECT * FROM '#' WHERE eventType = 'ENGINE_EXPLODED'"
  sql_version = "2016-03-23"

  firehose {
    delivery_stream_name = aws_kinesis_firehose_delivery_stream.s3_stream.name
    role_arn             = aws_iam_role.role.arn
    separator            = "\n"
  }

}


resource "aws_iam_role" "role" {
  name = "iot-to-kinesis-firehose"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "iot.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "iam_policy_for_iot_rule" {
  name = "mypolicy"
  role = aws_iam_role.role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["firehose:Put*"]
        Resource = [aws_kinesis_firehose_delivery_stream.s3_stream.arn]
      }
    ]

  })
}

data "aws_iot_endpoint" "endpoint" {
  endpoint_type = "iot:Data-ATS"
}

output "iot_endpoint" {
  value = data.aws_iot_endpoint.endpoint.endpoint_address
}

output "cert_private_key" {
  value     = aws_iot_certificate.cert.private_key
  sensitive = true
}

output "cert_public_key" {
  value     = aws_iot_certificate.cert.public_key
  sensitive = true
}

output "cert_pem" {
  value     = aws_iot_certificate.cert.certificate_pem
  sensitive = true
}
