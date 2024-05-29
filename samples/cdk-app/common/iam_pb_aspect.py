import re
import jsii
from aws_cdk import (
    CfnResource,
    IAspect,
    aws_iam as iam,
)
from pprint import pprint


@jsii.implements(IAspect)
class IamRolePermissionsBoundary:

    def visit(self, node) -> None:

        qualifier = node.node.try_get_context("@aws-cdk/core:bootstrapQualifier")
        if not qualifier:
            qualifier = "hnb659fds"

        if isinstance(node, iam.CfnRole):

            node.add_property_override(
                "PermissionsBoundary",
                f"arn:aws:iam::{node.stack.account}:policy/cdk-{qualifier}-app-permissions-boundary-{node.stack.account}-{node.stack.region}",
            )

        elif (
            isinstance(node, CfnResource) and node.cfn_resource_type == "AWS::IAM::Role"
        ):
            if re.match(r".+/Custom::.+CustomResourceProvider/Role$", node.node.path):
                node.add_property_override(
                    "PermissionsBoundary",
                    f"arn:aws:iam::{node.stack.account}:policy/cdk-{qualifier}-customresource-permissions-boundary-{node.stack.account}-{node.stack.region}",
                )
