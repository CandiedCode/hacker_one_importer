# Hacker One Importer
Service that imports hacker one reports from hackerone into jira

## Install requirements

### required
#### git
The docker image that gets pushed to production is tagged with the git commit hash

#### aws account / aws cli
This is required for the following actions
* To be able to setup aws infrastructure
* Connect to dynamodb
* access secrets 
* push to docker repository

#### docker
This is required for the following actions
* build production docker image
* to run locally 

#### make
A make file has been setup to streamline commands
```bash

# runs docker-compose file in development folder
make develop

# runs docker-compose down
make develop-down

# logs into aws ecr, required to push images
make docker-login

# build production docker image
make build-docker

# push docker image to ecr
make push

# terraform
make setup-terraform
```

#### optional
* python 3.6
* pycharm 


## setup cli
This service can be installed and run locally 

```bash
#install
python setup.py build install

#run options
h1 --help
Usage: h1 [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  activity_date
  imports
  
h1 imports --help
Usage: h1 imports [OPTIONS]

Options:
  --report_id INTEGER             Import a specific report id
  --last_activity TEXT            Last Activity Date to Import (YYYY-MM-DD
                                  HH:MM:SS (in UTC))
  --parallel / --not_parallel     Run in parallel mode
  --import_all                    Ignore last_activity date and import all
                                  hacker one reports
  --update_h1 / --do_not_update_h1
                                  do_not_update_h1 will prevent any updates to
                                  h1.  Which is updating issue_reference_id
  --ignore_dynamo                 ignore_dynamodb prevents the updating the
                                  last_activity_date in dynamodb
  --debug / --no-debug            Prints input flags
  --help                          Show this message and exit.
```
## Running via Docker Locally
A docker compose file has been setup in the development folder.  It will run a local instance of dynamodb.

```bash
make develop 
#or
cd development && docker-compose run --rm importer /bin/sh
```
This opens up the shell terminal inside the docker image. 

```bash
pytest  #runs python unit tests
h1 --help
h1 imports --help
python importer.py
```

## Useful Commands
```bash
   #invoke lambda call
   aws lambda invoke \
    --function-name=jira_import_lambda \
    --invocation-type=RequestResponse \
    --payload='{ "test": "value" }' \
    --log-type=Tail \
    /dev/null | jq -r '.LogResult' | base64 --decode
    
   # list information about ssms parameters in aws
   aws ssm describe-parameters
   
   # This will remove:
   #     - all stopped containers
   #     - all networks not used by at least one container
   #     - all volumes not used by at least one container
   #     - all dangling images
   #     - all build cache
   docker system prune --volumes

```