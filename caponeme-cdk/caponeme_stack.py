from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_ec2 as ec2,
    core
)


class CaponemeStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        ip_parameter = core.CfnParameter(self, "SSRFSGAllowedIP", type="String")
        instance_kp_parameter = core.CfnParameter(self, "SSRFInstanceKP", type="AWS::EC2::KeyPair::KeyName")

        ssrf_s3_bucket = s3.Bucket(self, "SSRFS3Bucket")

        ssrf_s3_policy = iam.Policy(self, "SSRFS3Policy",
            document=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["s3:ListBucket"],
                        resources=[ssrf_s3_bucket.bucket_arn]
                    ),
                    iam.PolicyStatement(
                        actions=["s3:GetObject"],
                        resources=[ssrf_s3_bucket.bucket_arn + "/*"]
                    )
                ]
            )
        )

        ssrf_s3_role = iam.Role(self, "SSRFS3Role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        ssrf_s3_role.add_managed_policy(policy=ssrf_s3_policy)

        vpc = ec2.Vpc(self, "VPC",
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC)]
            )

        ec2_machine_image = ec2.MachineImage.lookup(
            name="bitnami-lampstack*")

        ssrf_sg = ec2.SecurityGroup(self, "SSRFSG",
            description="Security Group that allows HTTP traffic",
            vpc=vpc
        )

        ssrf_sg.add_ingress_rule(peer=ec2.Peer.ipv4(ip_parameter.value_as_string + "/32"), connection=ec2.Port.tcp(port=80))

        with open("./caponeme-cdk/user_data.sh") as f:
            ec2_user_data = f.read()

        ssrf_instance = ec2.Instance(self, "SSRFInstance",
            vpc=vpc,
            security_group=ssrf_sg,
            instance_type=ec2.InstanceType(instance_type_identifier="t2.micro"),
            machine_image=ec2_machine_image,
            user_data=ec2.UserData.custom(ec2_user_data),
            role=ssrf_s3_role,
            key_name=instance_kp_parameter.value_as_string)

        output_bucket_name = core.CfnOutput(self, "SSRFS3BucketOutput", value=ssrf_s3_bucket.bucket_name)
        output_ssrf_web_url = core.CfnOutput(self, "SSRFWebURL", value="http://" + ssrf_instance.instance_public_dns_name)