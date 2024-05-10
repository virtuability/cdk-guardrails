from aws_cdk import App, Aspects, Stack

import pytest

from common.iam_path_aspect import IamPathFixer
from common.iam_pb_aspect import IamRolePermissionsBoundary
from stacks.sample_stack import SampleStack


@pytest.fixture()
def cdk_app() -> App:
    app = App()
    return app


@pytest.fixture()
def sample_stack(cdk_app) -> Stack:
    sample_stack = SampleStack(
        cdk_app, "SampleStack", env={"region": "us-east-1", "account": "123456789012"}
    )
    Aspects.of(sample_stack).add(IamPathFixer())
    Aspects.of(sample_stack).add(IamRolePermissionsBoundary())
    return sample_stack
