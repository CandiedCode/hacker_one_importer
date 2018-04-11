data "template_file" "jira_app" {
  template = "${file("${path.module}/jira_app.json.tpl")}"
  vars {
    REPOSITORY_URL = "${var.DOCKER_REPO}"
    DOCKER_TAG = "${var.DOCKER_TAG}"
    AWS_REGION = "${var.AWS_REGION}"
    LOGS_GROUP = "${aws_cloudwatch_log_group.jira-importer.name}"
  }
}

resource "aws_ecs_task_definition" "jira_app" {
  family                = "jira_import"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  container_definitions = "${data.template_file.jira_app.rendered}"
  execution_role_arn = "${aws_iam_role.ecs_task_assume.arn}"
  task_role_arn = "${aws_iam_role.jira-ecs-role.arn}"
}