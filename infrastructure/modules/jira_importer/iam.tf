resource "aws_iam_role" "ecs_task_assume" {
  name = "ecs_task_assume"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
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

resource "aws_iam_role_policy" "ecs_task_assume" {
  name = "ecs_task_assume"
  role = "${aws_iam_role.ecs_task_assume.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
             "Effect": "Allow",
             "Action": [
                 "ssm:DescribeParameters"
             ],
             "Resource": "*"
         }
    ]
}
EOF
}

resource "aws_iam_policy" "jira-importer-policy" {
    name = "JiraImporterPolicy"
    description = "Jira Importer Service Policy"
    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
         "Effect": "Allow",
         "Action": [
             "ssm:GetParameters"
         ],
         "Resource": [
             "${data.aws_ssm_parameter.password.arn}",
             "${data.aws_ssm_parameter.username.arn}",
             "${data.aws_ssm_parameter.token.arn}"
         ]
      },
      {
         "Effect": "Allow",
         "Action": [
             "kms:Decrypt"
         ],
         "Resource": [
             "${data.aws_kms_key.key.arn}"
         ]
      },
      {
         "Effect": "Allow",
         "Action": [
              "dynamodb:GetItem",
              "dynamodb:BatchGetItem",
              "dynamodb:BatchWriteItem",
              "dynamodb:UpdateTimeToLive",
              "dynamodb:PutItem",
              "dynamodb:Query",
              "dynamodb:UpdateItem",
              "dynamodb:CreateTable",
              "dynamodb:GetRecords"
         ],
         "Resource": [
             "${aws_dynamodb_table.jira-importer.arn}"
         ]
      }
    ]
  }
EOF
}

resource "aws_iam_role" "jira-ecs-role" {
    name = "JiraEcsRole"
    description = "Jira Importer Role"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
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

resource "aws_iam_policy_attachment" "jira-service-attach" {
    name = "jira-import-ecs-service-attach"
    roles = ["${aws_iam_role.jira-ecs-role.name}"]
    policy_arn = "${aws_iam_policy.jira-importer-policy.arn}"
}