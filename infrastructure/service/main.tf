provider "aws" {
    region    = "us-east-1"
}


terraform {
  backend "s3" {
      bucket = "tmna-infosec-tf"
      key    = "jira_importer_service.tfstate"
      region = "us-east-1"
      encrypt = "true"
      dynamodb_table = "terraform-lock"
    }
}

data "terraform_remote_state" "foundation" {
    backend = "s3"
    config {
        bucket = "tmna-infosec-tf"
        key = "jira_importer.tfstate"
        region = "us-east-1"
    }
}

# Create the foundation
module "jira_service" {
  source = "../modules/jira_importer",
  DOCKER_REPO = "${data.terraform_remote_state.foundation.jira-repo}"
  ECS_CLUSTER = "${data.terraform_remote_state.foundation.jira-cluster-id}"
  PRIVATE_SUBNET = "${data.terraform_remote_state.foundation.private-subnets}"
  SECURITY_GROUP = "${data.terraform_remote_state.foundation.security-group}"
  DOCKER_TAG = "${var.DOCKER_TAG}"
}

