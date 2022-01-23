import json

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_stepfunctions as stepfunctions,
    aws_stepfunctions_tasks as stepfunction_tasks,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_lambda as _lambda,
    aws_logs as logs
)
from constructs import Construct

class SubMinuteLambdaTrigger(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        interval: int,
        lambda_function: _lambda.Function,
        enabled=True,
         **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        seconds_per_minute = 60
        assert seconds_per_minute % interval == 0, "A minute has to be evenly divisible by interval! (60 mod interval = 0)"

        invocations_per_minute = int(seconds_per_minute / interval)
        wait_state_duration = interval

        wait_time_list = [
            wait_state_duration if i < (invocations_per_minute - 1) else 0
            for i in range(invocations_per_minute)            
        ]



        state_machine_definition = stepfunctions.Pass(
            scope=self,
            id="list-setup",
            comment="Sets up the number of invocations per minute",
            result=stepfunctions.Result(
                value={
                    "iterator": wait_time_list
                }
            )
        )

        state_machine_definition.next(
            stepfunctions.Map(
                scope=self,
                id="invoke-loop",
                comment="Invokes function and waits",
                max_concurrency=1,
                items_path="$.iterator",
            ).iterator(
                stepfunction_tasks.CallAwsService(
                    self,
                    "invoke-lambda-async",
                    action="invoke",
                    service="lambda",
                    iam_action="lambda:InvokeFunction",
                    iam_resources=[lambda_function.function_arn],
                    parameters={
                        "FunctionName": lambda_function.function_arn,
                        "InvocationType": "Event",
                    },
                    result_path=stepfunctions.JsonPath.DISCARD, # Discard the output and pass on the input
                ).next(
                    stepfunctions.Wait(
                        self,
                        "wait-until-next-iteration",
                        time=stepfunctions.WaitTime.seconds_path("$")
                    )
                )
            )
        )

        self.step_function = stepfunctions.StateMachine(
            self,
            id="sub-minute-trigger",
            definition=state_machine_definition,
            state_machine_name=lambda_function.function_name,
            state_machine_type=stepfunctions.StateMachineType.STANDARD,
            timeout=Duration.seconds(60),
            logs=stepfunctions.LogOptions(
                destination=logs.LogGroup(
                    self,
                    id="log-group-for-trigger",
                    removal_policy=RemovalPolicy.DESTROY,
                    retention=logs.RetentionDays.ONE_WEEK,
                )
            )
        )

        # Add trigger for each minute
        events.Rule(
            self,
            id="trigger",
            schedule=events.Schedule.expression("rate(1 minute)"),
            targets=[
                event_targets.SfnStateMachine(
                    self.step_function
                )
            ],
            enabled=enabled
        )



class SubMinuteLambdaTriggerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        lambda_function = _lambda.Function(
            self,
            "just-print",
            code=_lambda.Code.from_inline(
                code="""
def lambda_handler(event, context):
    print(event)
                """
            ),
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.lambda_handler"
        )

        # Create SubMinuteLambdaTrigger with Lambda Function and interval
        SubMinuteLambdaTrigger(
            self,
            "sub-minute-trigger",
            interval=10,
            lambda_function=lambda_function
        )

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "SubMinuteLambdaTriggerQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
