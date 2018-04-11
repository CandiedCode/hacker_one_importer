output "jira-repo" {
  value = "${aws_ecr_repository.jira_app.repository_url}"
}

output "jira-cluster-id" {
  value = "${aws_ecs_cluster.fargate.id}"
}

output "private-subnets" {
  value = "${module.base_vpc.private_subnets}"
}

output "security-group" {
  value = "${aws_security_group.ecs.id}"
}