from aws_cdk import Stack

import aws_cdk.assertions as assertions


def test_sample_policy(sample_stack: Stack):
    template = assertions.Template.from_stack(sample_stack)

    template.has_resource_properties(
        "AWS::IAM::ManagedPolicy",
        {
            "Path": "/apppolicies/",
        },
    )


def test_sample_role(sample_stack: Stack):
    template = assertions.Template.from_stack(sample_stack)

    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "Path": "/approles/",
            "RoleName": "SampleRole",
            "PermissionsBoundary": "arn:aws:iam::123456789012:policy/cdk-hnb659fds-permissions-boundary-123456789012-us-east-1",
        },
    )


def test_sample_lambda_role(sample_stack: Stack):
    template = assertions.Template.from_stack(sample_stack)

    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "PermissionsBoundary": "arn:aws:iam::123456789012:policy/cdk-hnb659fds-permissions-boundary-123456789012-us-east-1",
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                    },
                ]
            },
            "Path": "/approles/",
        },
    )
