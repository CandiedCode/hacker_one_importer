output "jira-repo" {
  value = "${module.jira_importer.jira-repo}"
}

output "jira-cluster-id" {
  value = "${module.jira_importer.jira-cluster-id}"
}

output "private-subnets" {
  value = "${module.jira_importer.private-subnets[0]}"
}

output "security-group" {
  value = "${module.jira_importer.security-group}"
}