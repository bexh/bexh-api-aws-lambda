# bexh-api-aws-lambda

## Project setup:

Virtual environment setup:

```

```

Install pipfile libraries:

```
make install-dev
```

### Set up interpreter:


Go to PyCharm > Settings > Project:bexh-api-aws-lambda > Project Interpreter

Select ... to the right of the option and select add...

Select existing environment

Select the python file as per your virtual environment which can be found using:

```
which python
```
Apply > Ok

### Configure Local Infra
Set up mysql and aws localstack containers and set up db tables:
```
make docker-up
make local-setup
```

## Running the Project

Open /service.py and hit the play button on the left hand side which will
use /event.json as the event to your function

## Configuring new routes

Locate the examples in /controllers.py

## Help

Make Targets:
```
Commands:
    build          Bundle package for deployment
    install        Installs pipfile libraries
    install-dev    Installs pipfile libraries for development purposes
    docker-up      Spins up localstack and mysql containers for local development
    docker-down    Spins down containers for local development
    local-setup    Creates a mysql instance and creates tables
    
```

Lambda Commands:
```
Commands:
  build      Bundles package for deployment.
  cleanup    Delete old versions of your functions
  deploy     Register and deploy your code to lambda.
  deploy-s3  Deploy your lambda via S3.
  init       Create a new function for Lambda.
  invoke     Run a local test of your function.
  upload     Upload your lambda to S3.
```

More info:

https://hackersandslackers.com/improve-your-aws-lambda-workflow-with-python-lambda/
  