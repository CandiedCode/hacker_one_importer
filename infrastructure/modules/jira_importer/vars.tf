variable "AWS_REGION" {
  type    = "string"
  default = "us-east-1"
}

variable "DOCKER_TAG" {
  type    = "string"
}

variable "DOCKER_REPO" {
  type    = "string"
}

variable "ECS_CLUSTER" {
  type    = "string"
}

variable "PRIVATE_SUBNET" {
}

variable "SECURITY_GROUP" {
  type    = "string"
}