from setuptools import setup

setup(
    name='bexh-api-aws-lambda',
    version='0.0.1',
    packages=[
        'package_name',
        'package_name.test'
    ],
    scripts=['bin/script1', 'bin/script2'],
    url='http://pypi.python.org/pypi/PackageName/',
    description='An awesome package that does something',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.1.1",
        "pytest",
    ],
)
