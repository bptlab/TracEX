# Set-Up

## Use PyCharm!

## Cloning

- run "git clone https://github.com/bptlab/TracEX"

## Requirements + Graphviz

- run "pip install -r requirements.txt"
- install graphviz like stated in https://graphviz.org/download/
(maybe set environment variable)
- set the environment variable

## Pre-Commit

- run "pre-commit install" in the root directory of TracEX

## Environment variables

- set variable: "OPENAI_API_KEY" with a personal key as value
- maybe set graphviz/bin in PATH

## Run as UI app

In the root directory (TracEX):
- run "cd tracex"
- run "python manage.py runserver"

## Run as command line app

- main config with "DJANGO_SETTINGS_MODULE=tracex.settings"
- run main
