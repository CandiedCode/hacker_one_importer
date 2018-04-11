provider "aws" {
    region    = "us-east-1"
}


terraform {
  backend "s3" {
      bucket = "tmna-infosec-tf"
      key    = "jira_importer.tfstate"
      region = "us-east-1"
      encrypt = "true"
      dynamodb_table = "terraform-lock"
    }
}

# Create the foundation
module "jira_importer" {
  source = "../modules/foundation",
}

