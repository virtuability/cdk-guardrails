from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
)
from constructs import Construct


class SampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        fn = _lambda.Function(
            self,
            "SampleLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                "def handler(event, context):\n  print('Hello, World!')"
            ),
            timeout=Duration.seconds(15),
        )

        policy = iam.ManagedPolicy(
            self,
            "SamplePolicy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["lambda:Invoke"],
                        resources=[fn.function_arn],
                    )
                ]
            ),
        )

        role = iam.Role(
            self,
            "SampleRole",
            assumed_by=iam.AccountPrincipal(self.account),
            role_name="SampleRole",
            managed_policies=[policy],
        )

        bucket = s3.Bucket(
            self,
            "SampleBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
