all: build deploy
ORIGIN ?= http://localhost:8080
ENV ?= aws
STACKNAME ?= vince-sam-app
DOCKER_NETWORK ?= lambda-network
TABLENAME ?= DynamoDbGreetingsTable
SAMCONFIG ?= samconfig
TEMPLATE ?= template
LOCAL_IP ?= 127.0.0.1

# Defines the default target that `make` will to try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = help

# The @ makes sure that the command itself isn't echoed in the terminal
help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make build"
	@echo "To deploy the project type make deploy"
	@echo "To destroy the project type make destroy"
	@echo "------------------------------------"

build:
	@echo "Building template $(TEMPLATE).yaml ..."
	@sam build -t $(TEMPLATE).yaml

tests:
	@env ENV=dev TABLE_NAME=$(TABLENAME) poetry run python -m pytest -v

localtest:
	@echo "SAM Local Testing first call"
	@ENABLE_LAMBDA_EXTENSIONS_PREVIEW=1 sam local invoke AddToGreetingsFunction --event events/event.json
	#@ENABLE_LAMBDA_EXTENSIONS_PREVIEW=1 sam local invoke ListGreetingsFunction --event events/event.json

deploy: build
	@echo "Deploying stack $(STACKNAME)-$(TEMPLATE) with $(SAMCONFIG)..."
	@sam deploy --config-file $(SAMCONFIG).toml --stack-name $(STACKNAME)-$(TEMPLATE) --parameter-overrides AllowedOrigin=$(ORIGIN) --parameter-overrides EnvParameter=$(ENV) --no-fail-on-empty-changeset

delete:
	@aws cloudformation delete-stack --stack-name $(STACKNAME)-$(TEMPLATE)
	@echo "Waiting for stack $(STACKNAME)-$(TEMPLATE) to be deleted..."
	@aws cloudformation wait stack-delete-complete --stack-name $(STACKNAME)-$(TEMPLATE)

describe:
	@aws cloudformation describe-stacks --stack-name $(STACKNAME)-$(TEMPLATE)

.PHONY: build package deploy delete