import jsii
from aws_cdk import (
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
