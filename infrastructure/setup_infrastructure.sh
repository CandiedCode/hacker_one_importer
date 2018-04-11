#!/bin/sh

#set -e
DOCKER_TAG=$1

if [ $# -eq 0 ]; then
    echo "Docker_Tag must be passed in."
    exit 1
fi

# Default Settings
TAG_OWNER="TMNA_InfoSec"
TAG_SYSTEM="JiraImporter"
TAG_ENV_NAME="Production"
S3_BUCKET="tmna-infosec-tf"
TAG_SET="TagSet=[{Key=OWNER,Value=$TAG_OWNER},{Key=SYSTEM,Value=$TAG_SYSTEM},{Key=ENV_NAME,Value=$TAG_ENV_NAME}]"
AWS_DEFAULT_REGION="us-east-1"
LOCK_TABLE="terraform-lock"

echo "--------------------------------------------------------------------------"
echo "---    Create AWS Infrastructure for JIRA_Importer :  Docker_Tag = ${DOCKER_TAG}  ---"
echo "--------------------------------------------------------------------------"


aws s3api head-bucket --bucket ${S3_BUCKET} 2>/dev/null

if [ $? == 255 ]; then
    echo "\t${S3_BUCKET} bucket does not exist"

    echo "--------------------------------"
    echo "---  Creating config bucket  ---"
    echo "--------------------------------"

    # Create Terraform State Bucket with versioning enabled, and tags set
    aws s3 mb s3://${S3_BUCKET} --region ${AWS_DEFAULT_REGION}
    aws s3api put-bucket-versioning --bucket ${S3_BUCKET} \
        --versioning-configuration Status=Enabled \
        --region ${AWS_DEFAULT_REGION}
    aws s3api put-bucket-tagging --bucket ${S3_BUCKET} \
        --tagging $TAG_SET \
        --region ${AWS_DEFAULT_REGION}

else
    echo "/t${S3_BUCKET} bucket already exists"
fi


# Check to see if lock table exists
aws dynamodb describe-table \
    --table-name $LOCK_TABLE \
    --region ${AWS_DEFAULT_REGION} > /dev/null 2>&1

if [  $? -eq 255 ]; then
    echo "-----------------------------------------"
    echo "---  Creating terraform lock table    ---"
    echo "-----------------------------------------"

    aws dynamodb create-table \
        --table-name $LOCK_TABLE \
        --attribute-definitions \
            AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region ${AWS_DEFAULT_REGION}
else
    echo "/t${LOCK_TABLE} dynamodb table already exists"
fi

echo "--------------------------------"
echo "---    Run Terraform init    ---"
echo "--------------------------------"

cd foundation && terraform init && terraform apply

echo "--------------------------------"
echo "---    Run Terraform apply   ---"
echo "--------------------------------"

cd ../service && terraform init && terraform apply -var "DOCKER_TAG=${DOCKER_TAG}"
