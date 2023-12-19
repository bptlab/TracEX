#!/bin/bash

sudo apt-get update && apt-get upgrade -y

sudo apt install python graphviz -y

pip install -r requirements.txt

