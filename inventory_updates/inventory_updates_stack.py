from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_stepfunctions as sfn,
    RemovalPolicy,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_dynamodb as dynamodb,
    Tags,
    aws_logs as logs,
    aws_pipes as pipes,
    aws_apigateway as apigw,
    aws_cognito as cognito
)
from constructs import Construct
from aws_cdk.aws_lambda import Function, Tracing


class InventoryUpdatesSystemStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "InventoryUpdatesSystemQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        
