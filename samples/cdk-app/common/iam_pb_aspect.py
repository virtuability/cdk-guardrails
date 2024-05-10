import jsii
from aws_cdk import (
    IAspect,
    aws_iam as iam,
)
from pprint import pprint


@jsii.implements(IAspect)
class IamRolePermissionsBoundary:

    def visit(self, node) -> None:

        if isinstance(node, iam.CfnRole):
            qualifier = node.node.try_get_context("@aws-cdk/core:bootstrapQualifier")
            if not qualifier:
                qualifier = "hnb659fds"
            node.add_property_override(
                "PermissionsBoundary",
                f"arn:aws:iam::{node.stack.account}:policy/cdk-{qualifier}-permissions-boundary-{node.stack.account}-{node.stack.region}",
            )
