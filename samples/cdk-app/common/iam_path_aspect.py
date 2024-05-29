import re
import jsii
from aws_cdk import (
    CfnResource,
    IAspect,
    aws_iam as iam,
)


@jsii.implements(IAspect)
class IamPathFixer:

    def visit(self, node) -> None:

        if isinstance(node, iam.CfnRole):

            if node.path in ["/", None]:
                node.add_property_override("Path", "/approles/")

        elif isinstance(node, iam.CfnManagedPolicy):

            if node.path in ["/", None]:
                node.add_property_override("Path", "/apppolicies/")

        elif isinstance(node, iam.CfnInstanceProfile):

            if node.path in ["/", None]:
                node.add_property_override("Path", "/appinstanceprofiles/")

        elif (
            isinstance(node, CfnResource) and node.cfn_resource_type == "AWS::IAM::Role"
        ):
            if re.match(r".+/Custom::.+CustomResourceProvider/Role$", node.node.path):
                node.add_property_override("Path", "/approles/")
