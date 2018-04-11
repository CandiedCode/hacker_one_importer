# Setting up AWS Infrastructure

## Setup

In order to run terraform modules, it is expected that a dynamo lock table and s3 state bucket have already been created.
These will get created via the setup_infrastructure script.

We also require that secrets are stored in the SSM Data store

```bash
#Example commands

aws ssm put-parameter --name TOKEN --value "somevalue" --type SecureString          #represents h1 api token
aws ssm put-parameter --name USERNAME --value "someuser" --type SecureString        #jira username
aws ssm put-parameter --name PASSWORD --value "somepassword" --type SecureString    #jira password

```

To standup aws infrastructure we just need to run
```bash
docker-compose run jira-terraform ./setup_infrastructure.sh $(git rev-parse --short HEAD)
```

The docker-compose file will mount the .aws/credentials file to use the aws key and secret of the default aws profile