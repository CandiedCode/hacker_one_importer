#############################################################################
# Make file for hacker_one_importer infrastructure
#
# Description:
# ------------
# This is for testing, building, and packaging hacker_one_importer
#
#
# Usage:
# ------
# 1. build-image will need to be run before any other targets are called
#
#
# Make Target:
# ------------
# The Makefile provides the following targets to make:
#   $ make build-docker
#
# Example:
# ------------
# make build
#############################################################################


.PHONY: build-docker, push, develop, develop-down, setup-terraform, docker-login

DOCKERTAG ?= $(shell git rev-parse --short HEAD)
AWS_ECR_REPO ?= $(shell aws ecr describe-repositories --query "repositories[?repositoryName=='jira_importer'].repositoryUri" --output text)

build-docker:
	${INFO} "Building hacker_one_importer Image $(DOCKERTAG)"
	@docker build --file=Dockerfile -t jira_importer:$(DOCKERTAG) .

push:
	@docker tag jira_importer:$(DOCKERTAG) ${AWS_ECR_REPO}:$(DOCKERTAG)
	@docker push ${AWS_ECR_REPO}:$(DOCKERTAG)

develop:
	${INFO} "Running Development Docker"
	cd development && docker-compose run --rm importer /bin/sh

develop-down:
	${INFO} "Running Development Compose Down"
	cd development && docker-compose down

setup-terraform:
	${INFO} "Building Terraform Image"
	cd infrastructure && docker-compose run jira-terraform ./setup_infrastructure.sh ${DOCKERTAG}

docker-login:
	aws ecr get-login --no-include-email --region us-east-1 | bash 2> /dev/null

aws-ecr:
	${INFO} $(AWS_ECR_REPO)



# Cosmetics
YELLOW := "\e[0;33m"
RED := "\e[0;31m"
NC := "\e[0m"

# Shell Functions
INFO := @bash -c '\
  printf $(YELLOW); \
  echo "=> $$@"; \
  printf $(NC)' SOME_VALUE