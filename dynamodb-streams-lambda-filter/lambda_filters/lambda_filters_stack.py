import json
import os

from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    # aws_sqs as sqs,
)
from constructs import Construct

import constants

class LambdaFiltersStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        data_table = dynamodb.Table(
            self,
            "data-table",
            table_name=f"{constants.APP_NAME}-data",
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
        )

        data_table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(name="GSI1PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="GSI1SK", type=dynamodb.AttributeType.STRING)
        )

        update_view_counters_lambda = _lambda.Function(
            self,
            id="update-view-counters",
            function_name=f"{constants.APP_NAME}-update-view-counters",
            environment={
                "TABLE_NAME": data_table.table_name,
            },
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                path=os.path.join(os.path.dirname(__file__), "..", "src")
            ),
            handler="update_view_counters.lambda_handler"
        )

        # Filters aren't yet (CDK v2.3.0) supported for DynamoDB, we have to
        # go to the low level CFN stuff here
        _lambda.CfnEventSourceMapping(
            self,
            id="update-view-counters-event-source",
            function_name=update_view_counters_lambda.function_name,
            event_source_arn=data_table.table_stream_arn,
            starting_position="LATEST",
            batch_size=1,
            filter_criteria={
                "Filters": [
                    {
                        "Pattern": json.dumps({
                            "dynamodb": {"NewImage": {"type": {"S": ["VIEW"]}}},  # Only capture view events here
                            "eventName": ["INSERT","REMOVE"],
                        })
                    }
                ]
            }
        )

        data_table.grant_read_write_data(update_view_counters_lambda)
        data_table.grant_stream_read(update_view_counters_lambda)

        update_like_counters_lambda = _lambda.Function(
            self,
            id="update-like-counters",
            function_name=f"{constants.APP_NAME}-update-like-counters",
            environment={
                "TABLE_NAME": data_table.table_name,
            },
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                path=os.path.join(os.path.dirname(__file__), "..", "src")
            ),
            handler="update_like_counters.lambda_handler"
        )

        # Filters aren't yet (CDK v2.3.0) supported for DynamoDB, we have to
        # go to the low level CFN stuff here
        _lambda.CfnEventSourceMapping(
            self,
            id="update-like-counters-event-source",
            function_name=update_like_counters_lambda.function_name,
            event_source_arn=data_table.table_stream_arn,
            starting_position="LATEST",
            batch_size=1,
            filter_criteria={
                "Filters": [
                    {
                        "Pattern": json.dumps({
                            "dynamodb": {"NewImage": {"type": {"S": ["VOTE"]}}},  # Only capture vote events here
                            "eventName": ["INSERT","REMOVE"],
                        })
                    }
                ]
            }
            
        )

        data_table.grant_read_write_data(update_like_counters_lambda)
        data_table.grant_stream_read(update_like_counters_lambda)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "LambdaFiltersQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
