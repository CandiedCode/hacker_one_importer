resource "aws_dynamodb_table" "jira-importer" {
  name           = "JiraImporter"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Project"

  attribute {
    name = "Project"
    type = "S"
  }

  tags {
    Name        = "jira-importer"
    Environment = "production"
  }
}