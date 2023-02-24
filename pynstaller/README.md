# Freezing Internet Tool
This is a brief guide to explain our step to make a binary file from fit.py. 
Below you find are the steps taken to create an executable on windows 11.


## Prerequisites
Make sure you have installed 'FIT' on your development machine as explained [here](https://github.com/fit-project/fit/).

## Install pyinstaller
There are two ways you can get the FIT:

### Cloning the github repository
The recommended way to get FIT is to use git to directly clone the FIT repository:

```
git clone git@github.com:fit-project/fit.git fit
```

This will clone the latest version of the FIT repository to a **fit** folder.


## Install
Once you've downloaded FIT and installed all the prerequisites:

* go in fit folder:
```
cd fit
```
* If you don't have [poetry](https://python-poetry.org/), install it (below its showed windows Powershell):
```
Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
* install the dependencies:
```
poetry install
```
## Running FIT

Run your application:

```
poetry run python fit.py
```
