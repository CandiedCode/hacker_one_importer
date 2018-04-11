resource "aws_kms_key" "key" {
  description             = "jira importer"
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "key" {
  name          = "alias/jira-import"
  target_key_id = "${aws_kms_key.key.key_id}"
}