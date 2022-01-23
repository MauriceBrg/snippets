# Snippets

This is a repository that contains code snippets, POCs and relatively small demos that I or other can use however they see fit.

## Index

- [Sub Minute Lambda Trigger](sub-minute-lambda-trigger/): CDK Construct that sets up a step function to trigger your lambda functions in intervals of less than a minute.
- [DynamoDB-Streams Lambda Filter Demo](dynamodb-streams-lambda-filter/): Demo of the new Lambda Filters for DynamoDB Streams (also available for SQS and Kinesis)
- [Glue Local](glue-local/): Setup to use Glue locally for development 
- [Python-PDF-Report](pdf/): Demo using `pdf-reports` to create pdf reports using python.
- [Terraform-VerneMQ-IoT-Core](terraform-vernemq-iot-core/): POC to bridge a local VerneMQ to AWS IoT Core, then filter the events and store them in a batched version (courtesy of Kinesis data firehose) in S3.
- [Terraform-SES](terraform-ses/): Two terraform modules + a demo that allow you to configure and use SES

