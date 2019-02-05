# Linux

`python -m fgo.agent`

## Requirements

Ubuntu 18.04 LTS: `sudo apt install python3.7 python3.7-venv`

## Virtualenv

Initial Creation: `virtualenv -p $(which python3.7) venv`

Activation: `source ./venv/bin/activate`

# Windows

## Requirements

Download and install:

1. [Python 3.7 x64 web installer](https://www.python.org/downloads/release/python-372/)

2. [Insomnia GraphQL client](https://insomnia.rest/download/#windows)

3. [Cmder Terminal Emulator](http://cmder.net/) (includes git, vim, bash)

4. Install virtualenv: `pip install virtualenv`

## Virtualenvs

Initial Creation: `virtualenv venv`

Activation: `venv/Scripts/activate`

Installation of packages: `pip install -r requirements-dev.txt`

## Starting the server

Using cmd or cmder:

```
(venv) λ set FLASK_ENV=development
(venv) λ set FLASK_APP=agent.py
(venv) λ flask run
```

# References

[Flask CLI](http://flask.pocoo.org/docs/dev/cli/)
