# aws-serverless-python-greetings

A simple server less project using AWS SAM, python 3.9 with poetry Function : say Greetings, but not all day long for you IP, using DynamoDB.

> Author: vincedgy

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. 

It includes the following files and folders.

- greetings-service - Code for the application's Lambda functions.
- events - Invocation events that you can use to invoke the functions.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions, API Gateway API, DynamoDB and so on.

Python 3.9 with Poetry is used (even if lambda supports here python 3.8).

These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

This code has been made within PyCharm bu can be developed with any other IDE.

* [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
* [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)


## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3.9 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)
* Poetry - [Install Poetry](https://python-poetry.org/docs/#installation)


# Makefile

A Makefile helps for all building and testing stages : 

```shell script
make build
```

- help : give you some advice
- build : runs `sam build --use-container` with proper variables
- localtest : runs `sam local invoke ...` with proper variables
- deploy : runs `sam deploy` with proper variables and the help of the `samconfig.toml`

Important Note : you'll need to make your own `samconfig.toml` file in order to SAM to build your assets within your S3 bucket.


With that, in order to build and deploy your application you should

## Install dependencies with poetry

```shell script
poetry install
```


## Build the project

```shell script
make build
```


## Ask SAM to make your`samconfig.toml`

```shell script
sam deploy --guided
```

Then follow steps and store the configuration in ```samconfig.toml``` :

> The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.


## Deploy the app

```shell script
make deploy
```

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Testing

### Unit testing 

Build the application and unit test (with pytest) it with 

```shell script
make tests
```

### Integration testing locally 

#### Launch local DynamoDB 

Using docker-compose you can launch a stack that will run a dynamoDb locally for your tests.

Note that we need to create a specific network in order to use the local dynamoDB

```shell script
docker network create --attachable aws-serverless-python-greetings_default
docker-compose up -d
```


Use dynamoDB_Greeting.json with AWS CLI for the table to be created

```shell script
aws dynamodb create-table \
    --cli-input-json file://dynamoDB_Greeting.json \
    --endpoint-url http://localhost:8000
```


Then you can use dynamodb-admin tool for local DynamoDB management

```shell script
env DYNAMO_ENDPOINT=http://localhost:8000 npx dynamodb-admin

npx: installed 103 in 10.872s
  database endpoint:    http://localhost:8000
  region:               eu-west-1
  accessKey:            AKIAXHIFPBTNOHR777UJ

  dynamodb-admin listening on http://localhost:8001 (alternatively http://0.0.0.0:8001)
``` 


You can ```http://localhost:8001``` to check out the DynamoDB table.


With all of that you launch tests with 

```shell script
make localtest
```

It tests a single function by invoking it directly with a test event. 
An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

```bash
AWS$ sam local invoke HelloWorldFunction --event events/event.json
```

### Test locally the API

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
AWS$ sam local start-api
AWS$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```


## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
AWS$ sam logs -n ListGreetingsFunction --stack-name AWS --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```bash
AWS$ pip install pytest pytest-mock --user
AWS$ python -m pytest tests/ -v
```

## Cleanup

To delete the application :

```bash
make delete
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)

