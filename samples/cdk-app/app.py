#!/usr/bin/env python3

from aws_cdk import (
    App,
    Aspects,
)

from common.iam_path_aspect import IamPathFixer
from common.iam_pb_aspect import IamRolePermissionsBoundary

from stacks.sample_stack import SampleStack


class Main:

    def __init__(self):

        self._app = App()

        sample_stack = SampleStack(
            self._app,
            "SampleStack",
            stack_name="Sample",
        )

        Aspects.of(sample_stack).add(IamPathFixer())
        Aspects.of(sample_stack).add(IamRolePermissionsBoundary())

        self._app.synth()


Main()
