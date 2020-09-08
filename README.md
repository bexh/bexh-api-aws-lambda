# bexh-api-aws-lambda

## Project setup:

Virtual environment setup:

```
pip3 install pipenv
pipenv shell --python 3.8
```

Install python-lambda:

```
pip3 install python-lambda
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

## Running the Project

Open /service.py and hit the play button on the left hand side which will
use /event.json as the event to your function

## Configuring new routes

Locate the examples in /controllers.py

## Help

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
  