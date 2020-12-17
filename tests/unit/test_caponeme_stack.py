import json
import pytest
import os

from aws_cdk import core
from caponeme_stack import CaponemeStack


def get_template():
    app = core.App()
    CaponemeStack(app, "caponeme", env={'account': os.environ['CDK_DEFAULT_ACCOUNT'], 'region': os.environ['CDK_DEFAULT_REGION']})
    return json.dumps(app.synth().get_stack("caponeme").template)


def test_ec2_instance_created():
    assert("AWS::EC2::Instance" in get_template())


def test_s3_bucket_created():
    assert("AWS::S3::Bucket" in get_template())
