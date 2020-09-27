from setuptools import setup

setup(
    name='bexh-api-aws-lambda',
    version='0.0.1',
    packages=[
        'main.src'
    ],
    scripts=[],
    url='http://pypi.python.org/pypi/PackageName/',
    description='An awesome package that does something',
    long_description=open('README.md').read(),
    install_requires=[
        "boto3",
        "pymysql"
    ],
)
