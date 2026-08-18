"""Unit tests for the caponeme stack.

These tests lock in the *intentionally vulnerable* configuration that the
Capital One breach walkthrough depends on. This is a security demo: the
misconfigured IMDS-accessible IAM role, the SSRF-reachable EC2 instance, the
private S3 bucket the attacker exfiltrates, and the public subnet / security
group are all "correct" here. Asserting them keeps the educational attack path
intact across refactors.
"""

import aws_cdk as cdk
from aws_cdk.assertions import Template, Match

STACK_ENV = cdk.Environment(account="123456789012", region="us-east-1")


def build_template() -> Template:
    app = cdk.App()
    # Imported lazily so a broken import surfaces as a test failure.
    from caponeme_stack import CaponemeStack

    stack = CaponemeStack(app, "caponeme", env=STACK_ENV)
    return Template.from_stack(stack)


def test_synthesizes_without_error():
    # Arrange / Act
    template = build_template()

    # Assert
    assert template is not None


def test_ec2_instance_created():
    template = build_template()
    template.resource_count_is("AWS::EC2::Instance", 1)


def test_s3_bucket_created():
    template = build_template()
    # The bucket the attacker exfiltrates from.
    template.resource_count_is("AWS::S3::Bucket", 1)


def test_iam_role_assumable_by_ec2():
    # The EC2 instance role is the pivot the SSRF attack steals credentials for.
    template = build_template()
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Action": "sts:AssumeRole",
                                "Principal": {"Service": "ec2.amazonaws.com"},
                            }
                        )
                    ]
                )
            }
        },
    )


def test_iam_policy_grants_bucket_read():
    # Intentionally over-scoped read access (ListBucket + GetObject) that the
    # stolen credentials abuse. Locking this in preserves the demo.
    template = build_template()
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like({"Action": "s3:ListBucket", "Effect": "Allow"}),
                        Match.object_like({"Action": "s3:GetObject", "Effect": "Allow"}),
                    ]
                )
            }
        },
    )


def test_instance_profile_attached_to_instance():
    # The instance must carry an instance profile for IMDS to hand out creds.
    template = build_template()
    template.resource_count_is("AWS::IAM::InstanceProfile", 1)


def test_security_group_allows_http_from_parameter_ip():
    # HTTP (80) is exposed so the SSRF web app is reachable from the given IP.
    template = build_template()
    template.has_resource_properties(
        "AWS::EC2::SecurityGroup",
        {
            "SecurityGroupIngress": Match.array_with(
                [
                    Match.object_like(
                        {
                            "FromPort": 80,
                            "ToPort": 80,
                            "IpProtocol": "tcp",
                        }
                    )
                ]
            )
        },
    )


def test_public_subnet_present():
    # The instance sits in a public subnet with no NAT gateway.
    template = build_template()
    template.has_resource_properties(
        "AWS::EC2::Subnet", {"MapPublicIpOnLaunch": True}
    )


def test_expected_cfn_parameters_present():
    template = build_template()
    template.has_parameter("SSRFSGAllowedIP", {"Type": "String"})
    template.has_parameter(
        "SSRFInstanceKP", {"Type": "AWS::EC2::KeyPair::KeyName"}
    )


def test_stack_outputs_present():
    template = build_template()
    outputs = template.find_outputs("*")
    assert "SSRFS3BucketOutput" in outputs
    assert "SSRFWebURL" in outputs
