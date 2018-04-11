data "template_file" "jira_lamda" {
  template = "${file("${path.module}/run_task.py.tpl")}"
  vars {
      ECS_CLUSTER = "${var.ECS_CLUSTER}"
      ECS_TASK_DEFINITION = "${aws_ecs_task_definition.jira_app.family}"
      #ECS_TASK_DEFINITION = "${aws_ecs_task_definition.jira_app.family}:${aws_ecs_task_definition.jira_app.revision}"
      PRIVATE_SUBNET = "${var.PRIVATE_SUBNET}"
      SECURITY_GROUP = "${var.SECURITY_GROUP}"
  }
}

data "archive_file" "init" {
  type        = "zip"
  output_path = "${path.module}/files/run_task_lambda.zip"
  source {
      content  = "${data.template_file.jira_lamda.rendered}"
      filename = "run_task.py"
    }
}


resource "aws_iam_role" "lambda_exec_role" {
  name = "LambdaJiraRole"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    },
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "jira-lambda-policy" {
    name = "JiraLambdaECSRunTask"
    description = "Jira Importer Service Policy"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:RunTask",
        "ecs:StartTask"
      ],
      "Resource": "*"
    },
    {
         "Sid":"",
         "Effect":"Allow",
         "Action":[
            "logs:PutLogEvents",
            "logs:CreateLogGroup",
            "logs:CreateLogStream"
         ],
         "Resource":"arn:aws:logs:us-east-1:*:*"
      }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "jira-lambda-attach" {
    name = "jira-lambda-service-attach"
    roles = ["${aws_iam_role.lambda_exec_role.name}"]
    policy_arn = "${aws_iam_policy.jira-lambda-policy.arn}"
}

resource "aws_lambda_function" "jira_import_lambda" {
    function_name = "jira_import_lambda"
    handler = "run_task.handler"
    runtime = "python3.6"
    filename = "${path.module}/files/run_task_lambda.zip"
    source_code_hash = "${base64sha256(file("${path.module}/files/run_task_lambda.zip"))}"
    role = "${aws_iam_role.lambda_exec_role.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.jira_import_lambda.function_name}"
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.jira_lambda_every_30_mins.arn}"
}

resource "aws_cloudwatch_event_rule" "jira_lambda_every_30_mins" {
    name = "jira-lambda-30-minutes"
    description = "Fires jira import every 30 minutes"
    schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "import_jira_lambda" {
    rule = "${aws_cloudwatch_event_rule.jira_lambda_every_30_mins.name}"
    arn = "${aws_lambda_function.jira_import_lambda.arn}"
}