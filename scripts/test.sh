#!/bin/bash -x
regions_array=(us-east-1 us-east-2 us-west-1 us-west-2 ca-central-1 eu-west-1 eu-west-2 eu-west-3 eu-central-1 eu-north-1 ap-northeast-1 ap-northeast-2 ap-south-1 ap-southeast-1 ap-southeast-2 sa-east-1)
for i in ${regions_array[@]}
do
  export CDK_DEFAULT_REGION=$i
  export CDK_DEFAULT_ACCOUNT="746046487306"
  export AWS_REGION=$i
  pytest .
done