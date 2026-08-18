#!/usr/bin/env python3
import os

import aws_cdk as cdk

from caponeme_stack import CaponemeStack

app = cdk.App()
CaponemeStack(app, "caponeme", env={'account': os.environ['CDK_DEFAULT_ACCOUNT'], 'region': os.environ['CDK_DEFAULT_REGION']})

app.synth()
