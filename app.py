#!/usr/bin/env python3
import os

from aws_cdk import core

from caponeme_stack import CaponemeStack    

app = core.App()
CaponemeStack(app, "caponeme", env={'account': os.environ['CDK_DEFAULT_ACCOUNT'], 'region': os.environ['CDK_DEFAULT_REGION']})

app.synth()
