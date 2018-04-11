data "aws_kms_key" "key" {
  key_id = "alias/jira-import"
}

data "aws_ssm_parameter" "username" {
  name  = "USERNAME"
}

data "aws_ssm_parameter" "password" {
  name  = "PASSWORD"
}

data "aws_ssm_parameter" "token" {
  name  = "TOKEN"
}