resource "aws_cloudwatch_log_group" "jira-importer" {
  name              = "/ecs/jira-importer"
  retention_in_days = 30
  tags {
    Name = "jira-importer"
  }
}

resource "aws_cloudwatch_log_group" "jira-import_lambda" {
  name              = "/aws/lambda/jira_import_lambda"
  retention_in_days = 30
  tags {
    Name = "jira-importer"
  }
}