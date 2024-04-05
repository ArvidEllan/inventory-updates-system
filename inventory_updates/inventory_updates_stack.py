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

        # Create a role for the Lambda function
        role = iam.Role(
            self, "InventoryFunctionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="InventoryFunctionRole",
            description="Role for Lambda functions"
        )
        Tags.of(role).add("department", "inventory")

        # Allow the Lambda function to write to CloudWatch Logs
        role.add_to_policy(iam.PolicyStatement(
            actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=["arn:aws:logs:*:*:*"]
        ))
      # Create the Dead Letter Queue (DLQ)
        dlq = sqs.Queue(self, 'InventoryUpdatesDlq',
            visibility_timeout=Duration.seconds(300)
        )
        Tags.of(dlq).add("department", "inventory")
        
        # Create the cognito userpool
        
        user_pool = cognito.UserPool(self, "UserPool",
                                     user_pool_name="well-architect-user-pool",
                                     self_sign_up_enabled=True,
                                     sign_in_aliases=cognito.SignInAliases(email=True),
                                     standard_attributes=cognito.StandardAttributes(
                                         email=cognito.StandardAttribute(mutable=True, required=True)
                                     )
                                     )
        cognito.UserPoolClient(self, "UserPoolClient", user_pool=user_pool)
        auth = apigw.CognitoUserPoolsAuthorizer(self, "Authorizer", cognito_user_pools=[user_pool] )
        # Create the SQS queue with DLQ setting
        queue = sqs.Queue(
            self, "InventoryUpdatesQueue",
            visibility_timeout=Duration.seconds(300),
            encryption=sqs.QueueEncryption.KMS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=2,  # Number of retries before sending the message to the DLQ
                queue=dlq
            )
        )

        # Create an SQS queue policy to allow source queue to send messages to the DLQ
        policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["sqs:SendMessage"],
            resources=[dlq.queue_arn],
            conditions={"ArnEquals": {"aws:SourceArn": queue.queue_arn}},
        )
        queue.queue_policy = iam.PolicyDocument(statements=[policy])
        Tags.of(queue).add("department", "inventory")



    

        
